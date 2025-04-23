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

    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot', 'judges', 'is_ready', 'is_full']

    def get_judges(self, obj):
        judge_entries = Judge.objects.select_related("user").filter(tribunal=obj)
        return JudgeSerializer(judge_entries, many=True).data

    def get_is_ready(self, obj):
        return obj.is_ready()

    def get_is_full(self, obj):
        return obj.is_full()


class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot']
    
    def validate_slot(self, slot):
        if self.instance and self.instance.slot == slot:
            return slot

        if slot.is_full():
            raise serializers.ValidationError("This slot has reached its maximum number of TFMs.")
        return slot
    
    def create(self, validated_data):
        tribunal = super().create(validated_data)
        self._recalculate_slot_end_time(tribunal.slot)
        return tribunal

    def update(self, instance, validated_data):
        original_slot = instance.slot
        new_slot = validated_data.get('slot', original_slot)

        instance = super().update(instance, validated_data)

        # If slot was changed, update both old and new slot end times
        if original_slot != new_slot:
            self._recalculate_slot_end_time(original_slot)
            self._recalculate_slot_end_time(new_slot)

        return instance

    def _recalculate_slot_end_time(self, slot):
        tfm_count = slot.tribunals.count()
        if tfm_count == 0:
            slot.end_time = slot.start_time  # Reset to start time if empty (optional behavior)
        else:
            total_duration = tfm_count * slot.tfm_duration
            slot.end_time = (
                datetime.combine(date.today(), slot.start_time) + total_duration
            ).time()
        slot.save(update_fields=["end_time"])