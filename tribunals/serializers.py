from rest_framework import serializers
from .models import Tribunal
from tfms.serializers import TFMReadSerializer
from slots.serializers import SlotSerializer
from users.serializers import UserSerializer
from judges.models import Judge
from judges.serializers import JudgeSerializer
from datetime import datetime, date

class TribunalReadSerializer(serializers.ModelSerializer):
    tfm = TFMReadSerializer()
    slot = SlotSerializer()
    judges = serializers.SerializerMethodField()
    is_ready = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot', 'judges', 'is_ready', 'is_full', 'start_time', 'end_time', 'index']

    def get_judges(self, obj):
        judge_entries = Judge.objects.select_related("user").filter(tribunal=obj)
        return JudgeSerializer(judge_entries, many=True).data

    def get_is_ready(self, obj):
        return obj.is_ready()

    def get_is_full(self, obj):
        return obj.is_full()

    def get_start_time(self, obj):
        base_time = datetime.combine(date.today(), obj.slot.start_time)
        tribunal_start = base_time + ((obj.index - 1) * obj.slot.tfm_duration)
        return tribunal_start.strftime("%H:%M")

    def get_end_time(self, obj):
        base_time = datetime.combine(date.today(), obj.slot.start_time)
        tribunal_end = base_time + (obj.index * obj.slot.tfm_duration)
        return tribunal_end.strftime("%H:%M")


class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot', 'index']

    def validate(self, attrs):
        index = attrs.get('index', self.instance.index if self.instance else None)
        slot = attrs.get('slot', self.instance.slot if self.instance else None)

        if not slot:
            raise serializers.ValidationError("Slot is required.")

        if index:
            self._validate_index(index, slot, self.instance)

        return attrs

    def validate_slot(self, slot):
        if self.instance and self.instance.slot == slot:
            return slot
        if slot.is_full():
            raise serializers.ValidationError("This slot has reached its maximum number of TFMs.")
        return slot

    def create(self, validated_data):
        if 'index' not in validated_data:
            slot = validated_data['slot']
            taken_indexes = set(slot.tribunals.values_list('index', flat=True))
            for i in range(1, slot.max_tfms + 1):
                if i not in taken_indexes:
                    validated_data['index'] = i
                    break
            else:
                raise serializers.ValidationError("No available index in this slot.")

        tribunal = super().create(validated_data)
        self._recalculate_slot_end_time(tribunal.slot)
        return tribunal

    def update(self, instance, validated_data):
        if 'index' in validated_data:
            self._validate_index(validated_data['index'], validated_data.get('slot', instance.slot), instance)

        original_slot = instance.slot
        new_slot = validated_data.get('slot', original_slot)

        instance = super().update(instance, validated_data)

        if original_slot != new_slot:
            self._recalculate_slot_end_time(original_slot)
        self._recalculate_slot_end_time(new_slot)

        return instance

    def _validate_index(self, index, slot, instance=None):
        if index < 1 or index > slot.max_tfms:
            raise serializers.ValidationError(f"Index must be between 1 and {slot.max_tfms}.")
        qs = slot.tribunals.exclude(pk=instance.pk if instance else None)
        if qs.filter(index=index).exists():
            raise serializers.ValidationError(f"Index {index} is already taken for this slot.")

    def _recalculate_slot_end_time(self, slot):
        tfm_count = slot.tribunals.count()
        if tfm_count == 0:
            slot.end_time = slot.start_time
        else:
            total_duration = tfm_count * slot.tfm_duration
            slot.end_time = (
                datetime.combine(date.today(), slot.start_time) + total_duration
            ).time()
        slot.save(update_fields=["end_time"])
