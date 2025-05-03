from rest_framework import serializers
from .models import Profile
from django.contrib.auth import get_user_model
from institutions.serializers import InstitutionSerializer

User = get_user_model()

class ProfileReadSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = instance.user
        representation['user'] = {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
        }
        return representation

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'institution', 'photo']