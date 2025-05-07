from rest_framework import serializers
from .models import TeacherApplication
from users.serializers import UserSerializer
from institutions.serializers import InstitutionSerializer

class TASerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = TeacherApplication
        fields = ['id', 'user', 'institution', 'attachment', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'created_at']


class TAUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TeacherApplication
        fields = ['email', 'status', 'attachment', 'institution']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        if new_status == TeacherApplication.APPROVED:
            instance.approve()
        elif new_status == TeacherApplication.REJECTED:
            instance.reject()

        # Update other fields
        instance.attachment = validated_data.get('attachment', instance.attachment)
        instance.institution = validated_data.get('institution', instance.institution)
        instance.save()
        return instance
