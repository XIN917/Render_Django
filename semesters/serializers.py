from rest_framework import serializers
from .models import Semester

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format time fields as HH:MM
        for field in ['daily_start_time', 'daily_end_time', 'pre_duration']:
            value = data.get(field)
            if value:
                data[field] = value[:5]  # Truncate to HH:MM
        return data
