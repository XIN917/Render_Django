from rest_framework import serializers
from .models import Slot
from tfms.serializers import TFMReadSerializer
from datetime import time

class SlotSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source="track.title", read_only=True)
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Slot
        fields = '__all__'

    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        room = data.get('room')
        date = data.get('date') or (self.instance.date if self.instance else None)
        track = data.get('track') or (self.instance.track if self.instance else None)

        if not track or not track.semester:
            raise serializers.ValidationError("Slot must be linked to a track with a valid semester.")

        semester = track.semester

        # Basic time bounds
        if start_time and start_time < semester.daily_start_time:
            raise serializers.ValidationError({'start_time': "Start time is before semester's allowed presentation time."})
        if end_time and end_time > semester.daily_end_time:
            raise serializers.ValidationError({'end_time': "End time is after semester's allowed presentation time."})
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': "End time must be after start time."})

        # Presentation date validation
        if date:
            if not (semester.int_presentation_date <= date <= semester.last_presentation_date):
                raise serializers.ValidationError({'date': "Slot date is outside the allowed presentation window."})
            if date.weekday() >= 5:
                raise serializers.ValidationError({'date': "Slot date cannot fall on a weekend."})

        # Overlap check
        if start_time and end_time and room and date:
            overlapping = Slot.objects.filter(
                date=date,
                room=room,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError("This time slot overlaps with another slot in the same room.")

        # Check if time fits max TFMs
        duration = semester.pre_duration
        max_tfms = data.get('max_tfms', self.instance.max_tfms if self.instance else 2)
        total_required_seconds = duration.total_seconds() * max_tfms
        actual_slot_seconds = (
            (end_time.hour * 60 + end_time.minute) -
            (start_time.hour * 60 + start_time.minute)
        ) * 60

        if total_required_seconds > actual_slot_seconds:
            raise serializers.ValidationError("Slot does not have enough time to accommodate all TFMs.")

        return data

    def create(self, validated_data):
        slot = Slot(**validated_data)
        slot.full_clean()  # triggers model-level validation
        slot.save()
        return slot

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


class SlotReadSerializer(serializers.ModelSerializer):
    tfms = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')
    tfm_duration = serializers.SerializerMethodField()
    track_title = serializers.CharField(source="track.title", read_only=True)

    class Meta:
        model = Slot
        fields = '__all__'

    def get_tfms(self, obj):
        return TFMReadSerializer(obj.get_tfms(), many=True).data

    def get_is_full(self, obj):
        return obj.is_full()

    def get_tfm_duration(self, obj):
        duration = obj.track.semester.pre_duration
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}"
