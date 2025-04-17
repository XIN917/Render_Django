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

    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot', 'judges']

    def get_judges(self, obj):
        judge_entries = Judge.objects.filter(tribunal=obj)
        return JudgeSerializer(judge_entries, many=True).data

class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot']
