from rest_framework import serializers
from .models import Slot
from tfms.serializers import TFMReadSerializer
from datetime import time

class SlotSerializer(serializers.ModelSerializer):
    presentation_date = serializers.DateField(source="presentation_day.date", read_only=True)
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
        presentation_day = data.get('presentation_day')

        # Time format validation
        if start_time and start_time.minute not in (0, 30):
            raise serializers.ValidationError({'start_time': "Start time must be on the hour or half-hour."})
        if end_time and end_time.minute not in (0, 30):
            raise serializers.ValidationError({'end_time': "End time must be on the hour or half-hour."})
        if start_time and start_time < time(8, 0):
            raise serializers.ValidationError({'start_time': "Start time must be after 08:00."})
        if end_time and end_time > time(21, 0):
            raise serializers.ValidationError({'end_time': "End time must be before 21:00."})
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': "End time must be after start time."})

        # Overlapping check
        if start_time and end_time and room and presentation_day:
            overlapping = Slot.objects.filter(
                presentation_day=presentation_day,
                room=room,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError("This time slot overlaps with another slot in the same room.")

        return data

class SlotReadSerializer(serializers.ModelSerializer):
    tfms = serializers.SerializerMethodField()
    presentation_date = serializers.DateField(source="presentation_day.date", read_only=True)
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
        total_seconds = int(obj.tfm_duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}"
