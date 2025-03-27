from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TFM, TFMReview
from users.serializers import UserSerializer

User = get_user_model()

class TFMReviewSerializer(serializers.ModelSerializer):
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TFMReview
        fields = ['reviewed_at', 'reviewed_by', 'action', 'comment']


class TFMSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    directors = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'), many=True, required=False)
    review = TFMReviewSerializer(read_only=True)

    class Meta:
        model = TFM
        fields = [
            'id', 'title', 'description', 'file', 'attachment',
            'created_at', 'status', 'student', 'directors', 'review',
        ]
        read_only_fields = ['status', 'created_at', 'review']

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        title = attrs.get("title") or self.instance.title if self.instance else None
        student = attrs.get("student") or self.instance.student if self.instance else (user if user.role == User.STUDENT else None)
        directors = attrs.get("directors") or list(self.instance.directors.all()) if self.instance else []

        if not student:
            raise serializers.ValidationError({"student": "A student must be assigned."})

        if not directors and not (user.role == User.TEACHER and not user.is_staff and not user.is_superuser):
            raise serializers.ValidationError({"directors": "At least one director must be assigned."})

        # 🛡️ Prevent duplicate, excluding self if editing
        existing_tfms = TFM.objects.filter(title=title, student=student).exclude(pk=getattr(self.instance, "pk", None))
        for tfm in existing_tfms:
            existing_directors = set(tfm.directors.values_list("id", flat=True))
            incoming_directors = set(d.id for d in directors)
            if existing_directors == incoming_directors:
                raise serializers.ValidationError({
                    "non_field_errors": ["This TFM with same title, student, and directors already exists."]
                })

        return attrs

    def validate_directors(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("A TFM can have a maximum of 2 directors.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        provided_directors = validated_data.pop("directors", [])

        # Auto assign student if not admin
        if not validated_data.get("student") and user.role == User.STUDENT:
            validated_data["student"] = user

        # Auto assign director if teacher and no explicit directors
        if not provided_directors and user.role == User.TEACHER and not user.is_staff and not user.is_superuser:
            provided_directors = [user]

        if not provided_directors:
            raise serializers.ValidationError({"directors": "At least one director must be assigned."})

        tfm = TFM.objects.create(**validated_data)
        tfm.directors.set(provided_directors)

        # Status based on role
        tfm.status = "approved" if user.role in [User.TEACHER] or user.is_staff else "pending"
        tfm.save()
        return tfm


class TFMReadSerializer(serializers.ModelSerializer):
    student = UserSerializer()
    directors = UserSerializer(many=True)
    review = TFMReviewSerializer(read_only=True)

    class Meta:
        model = TFM
        fields = [
            'id', 'title', 'description', 'file', 'attachment',
            'created_at', 'status', 'student', 'directors', 'review',
        ]
