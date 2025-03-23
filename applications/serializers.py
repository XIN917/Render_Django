from rest_framework import serializers
from .models import TeacherApplication
from users.serializers import UserSerializer

class TASerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TeacherApplication
        fields = ['id', 'user', 'certificate', 'additional_info', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'created_at']


class TAUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TeacherApplication
        fields = ['email', 'status']  # Only email and status fields

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            if validated_data['status'] == TeacherApplication.APPROVED:
                instance.approve()
            elif validated_data['status'] == TeacherApplication.REJECTED:
                instance.reject()
        return instance
