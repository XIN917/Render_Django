from rest_framework import serializers
from .models import Track
from slots.serializers import SlotReadSerializer

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = '__all__'


class TrackReadSerializer(serializers.ModelSerializer):
    slots = SlotReadSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = '__all__'
