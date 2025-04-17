from rest_framework import serializers
from .models import Tribunal, TribunalMember
from tfms.serializers import TFMReadSerializer
from slots.serializers import SlotSerializer
from users.serializers import UserSerializer
from users.models import User


class TribunalMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TribunalMember
        fields = ['user', 'role']


class TribunalReadSerializer(serializers.ModelSerializer):
    tfm = TFMReadSerializer()
    slot = SlotSerializer()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot', 'members']

    def get_members(self, obj):
        members = TribunalMember.objects.filter(tribunal=obj)
        return TribunalMemberSerializer(members, many=True).data


class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = ['id', 'tfm', 'slot']

class AssignTribunalRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TribunalMember
        fields = ['tribunal', 'user', 'role']

    def validate(self, data):
        role = data['role']
        tribunal = data['tribunal']
        user = data['user']

        if TribunalMember.objects.filter(tribunal=tribunal, user=user).exists():
            raise serializers.ValidationError("This user is already a member of this tribunal.")

        if role in ['president', 'secretary']:
            if TribunalMember.objects.filter(tribunal=tribunal, role=role).exists():
                raise serializers.ValidationError(f"The role '{role}' is already taken in this tribunal.")

        if user.is_superuser:
            raise serializers.ValidationError("Superusers cannot be assigned to tribunals.")

        return data
