from rest_framework import serializers
from .models import TFM, Director, TFMReview
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()

class TFMReviewSerializer(serializers.ModelSerializer):
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TFMReview
        fields = ['reviewed_at', 'reviewed_by', 'action', 'comment']


class DirectorReadSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Director
        fields = ['id', 'user']


class TFMSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    directors = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher', is_staff=False),
        many=True,
        required=False
    )
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

        title = attrs.get("title")
        student = attrs.get("student") or (user if user.role == User.STUDENT else None)
        directors = attrs.get("directors") or []

        if not student:
            raise serializers.ValidationError({"student": "A student must be assigned."})

        if not directors and not (user.role == User.TEACHER and not user.is_staff and not user.is_superuser):
            raise serializers.ValidationError({"directors": "At least one director must be assigned."})

        # Prevent duplicate
        existing_tfms = TFM.objects.filter(title=title, student=student)
        for tfm in existing_tfms:
            existing_directors = set(tfm.directors.values_list("user_id", flat=True))
            incoming_directors = set([d.id for d in directors])
            if existing_directors == incoming_directors:
                raise serializers.ValidationError(
                    "This TFM with the same title, student, and director combination already exists."
                )

        return attrs

    def validate_directors(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("A TFM can have a maximum of 2 directors.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        provided_directors = validated_data.pop("directors", [])

        # Assign student if not provided and user is student
        if not validated_data.get("student") and user.role == User.STUDENT:
            validated_data["student"] = user

        # Resolve final directors BEFORE creating the TFM
        final_directors = []

        if provided_directors:
            final_directors = Director.objects.filter(user__in=provided_directors)
        elif user.role == User.TEACHER and not user.is_staff and not user.is_superuser:
            auto_director = Director.objects.filter(user=user).first()
            if auto_director:
                final_directors = [auto_director]

        if not final_directors:
            raise serializers.ValidationError({"directors": "At least one director must be assigned."})

        # ✅ Only now create the TFM after validation
        tfm = TFM.objects.create(**validated_data)
        tfm.directors.set(final_directors)

        # Set status
        if user.is_staff or user.is_superuser:
            tfm.status = "approved"
        elif user.role == User.TEACHER:
            tfm.status = "approved"
        else:
            tfm.status = "pending"

        tfm.save()
        return tfm


class TFMReadSerializer(serializers.ModelSerializer):
    student = UserSerializer()
    directors = DirectorReadSerializer(many=True)
    review = TFMReviewSerializer(read_only=True)

    class Meta:
        model = TFM
        fields = [
            'id', 'title', 'description', 'file', 'attachment',
            'created_at', 'status', 'student', 'directors', 'review',
        ]
