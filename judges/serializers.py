from rest_framework import serializers
from .models import Judge
from users.serializers import UserSerializer

class JudgeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Judge
        fields = ['user', 'role', 'tribunal']


class AssignJudgeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Judge
        fields = ['tribunal', 'user', 'role']
    
    def validate_user(self, value):
        if value.role != 'teacher':
            raise serializers.ValidationError("Only users with the role 'teacher' can be assigned as judges.")
        return value

    def validate(self, data):
        role = data['role']
        tribunal = data['tribunal']
        user = data['user']

        if Judge.objects.filter(tribunal=tribunal, user=user).exists():
            raise serializers.ValidationError("This user is already assigned to this tribunal.")

        if role in ['president', 'secretary']:
            if Judge.objects.filter(tribunal=tribunal, role=role).exists():
                raise serializers.ValidationError(f"The role '{role}' is already taken in this tribunal.")

        if user.is_superuser:
            raise serializers.ValidationError("Superusers cannot be assigned to tribunals.")

        return data
