from rest_framework import serializers
from .models import TeacherApplication
from users.serializers import UserSerializer  # Import UserSerializer for nested representation

class TASerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Display user details

    class Meta:
        model = TeacherApplication
        fields = ['id', 'user', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'created_at']


class TAUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherApplication
        fields = ['status']

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            if validated_data['status'] == TeacherApplication.APPROVED:
                instance.approve()
            elif validated_data['status'] == TeacherApplication.REJECTED:
                instance.reject()
        return instance
