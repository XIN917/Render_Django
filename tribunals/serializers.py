from rest_framework import serializers
from .models import Tribunal

class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = '__all__'
