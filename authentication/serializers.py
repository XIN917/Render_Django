from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'password', 'role')
        extra_kwargs = {
            'role': {'read_only': True},
            'email': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Custom JWT Token Serializer to include the user's role, is_superuser, and is_staff """
    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        data["is_superuser"] = self.user.is_superuser
        data["is_staff"] = self.user.is_staff
        return data

class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        user = User.objects.filter(email=data["email"]).first()
        if not user:
            raise serializers.ValidationError("User not found.")
        if user.password:
            raise serializers.ValidationError("You already have a password. Use password reset instead.")
        return {"user": user, "password": data["password"]}

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password"])
        user.save()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        """Ensure old password is correct, new passwords match, and new password is not the same as the old one."""
        user = self.context['request'].user

        # Check if old password is correct
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Incorrect old password."})

        # Ensure new password and confirm password match
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Ensure the new password is not the same as the old password
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the old password."})

        return data

    def save(self, **kwargs):
        """Set the new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
