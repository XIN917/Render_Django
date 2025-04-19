from rest_framework import serializers
from .models import Tribunal
from tfms.serializers import TFMReadSerializer
from slots.serializers import SlotSerializer
from users.serializers import UserSerializer
from judges.models import Judge
from judges.serializers import JudgeSerializer

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
