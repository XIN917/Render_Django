from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    bio = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = ['id', 'email', 'full_name', 'role', 'bio']
