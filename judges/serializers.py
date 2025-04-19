from rest_framework import serializers
from .models import Judge
from users.serializers import UserSerializer

class JudgeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Judge
        fields = '__all__'


class AssignJudgeRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Judge
        fields = '__all__'
    
    def validate_user(self, value):
        if value.role != 'teacher':
            raise serializers.ValidationError("Only users with the role 'teacher' can be assigned as judges.")
        return value

    def validate(self, data):
        role = data['role']
        tribunal = data['tribunal']
        user = data['user']

        # When updating, exclude the current instance from validation checks
        existing_judge_qs = Judge.objects.filter(tribunal=tribunal, user=user)
        if self.instance:
            existing_judge_qs = existing_judge_qs.exclude(pk=self.instance.pk)

        if existing_judge_qs.exists():
            raise serializers.ValidationError("This user is already assigned to this tribunal.")

        if role in ['president', 'secretary']:
            role_taken_qs = Judge.objects.filter(tribunal=tribunal, role=role)
            if self.instance:
                role_taken_qs = role_taken_qs.exclude(pk=self.instance.pk)

            if role_taken_qs.exists():
                raise serializers.ValidationError(f"The role '{role}' is already taken in this tribunal.")

        if user.is_superuser:
            raise serializers.ValidationError("Superusers cannot be assigned to tribunals.")

        return data
