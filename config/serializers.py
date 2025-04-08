from rest_framework import serializers
from .models import PresentationDay

class PresentationDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationDay
        fields = ['id', 'date']
