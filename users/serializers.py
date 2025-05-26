from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import Profile
from institutions.models import Institution

User = get_user_model()

### 🟢 CREATE USER SERIALIZER ###
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'is_staff', 'is_superuser', 'institution']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        role = attrs.get('role', User.STUDENT)
        institution = attrs.get('institution', None)

        if attrs.get('is_superuser', False) and role == User.STUDENT:
            raise serializers.ValidationError({"role": "Superusers cannot have the 'student' role."})

        if role == User.TEACHER and not institution:
            raise serializers.ValidationError({"institution": "Institution must be set when creating a teacher."})

        return attrs

    def create(self, validated_data):
        institution = validated_data.pop('institution', None)
        password = validated_data.pop('password', None) or "12345678"

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == User.TEACHER:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.institution = institution
            profile.save()

        return user


### 🟡 GENERAL USER SERIALIZER ###
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for getting, updating, and deleting users.
    """
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # Ensure password is hashed

        instance.save()
        return instance

### 🔴 USER SELF UPDATE SERIALIZER ###
class UserSelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'email']
        read_only_fields = ['email']  # ✅ make email read-only

