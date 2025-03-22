from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

### 🟢 CREATE USER SERIALIZER ###
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'is_staff', 'is_superuser']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs.get('is_superuser', False) and attrs.get('role') == User.STUDENT:
            raise serializers.ValidationError({"role": "Superusers cannot have the 'student' role."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None) or "12345678"  # Set default password if not provided
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
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

