from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TFM, TFMReview
from users.serializers import UserSerializer
from semesters.models import Semester
from django.utils import timezone

User = get_user_model()


class TFMReviewSerializer(serializers.ModelSerializer):
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TFMReview
        fields = ['reviewed_at', 'reviewed_by', 'action', 'comment']


class TFMSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    directors = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'), many=True, required=False)
    review = TFMReviewSerializer(read_only=True)

    class Meta:
        model = TFM
        fields = [
            'id', 'title', 'description', 'file', 'attachment',
            'created_at', 'status', 'author', 'directors', 'review',
        ]
        read_only_fields = ['status', 'created_at', 'review']

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user

        # Safely determine title
        title = attrs.get("title") or (self.instance.title if self.instance else None)

        # Determine author
        if "author" in attrs:
            author = attrs["author"]
        elif self.instance:
            author = self.instance.author
        elif user.role == User.STUDENT:
            author = user
        else:
            author = None

        # Determine directors
        if "directors" in attrs:
            directors = attrs["directors"]
        elif self.instance:
            directors = list(self.instance.directors.all())
        else:
            directors = []

        # Validate author presence
        if not author:
            raise serializers.ValidationError({"author": "An author (student) must be assigned."})

        # Validate director rules
        if not directors and not (user.role == User.TEACHER or user.is_superuser):
            raise serializers.ValidationError({"directors": "At least one director must be assigned."})

        # 🛡️ Prevent duplicate
        existing_tfms = TFM.objects.filter(title=title, author=author).exclude(pk=getattr(self.instance, "pk", None))
        for tfm in existing_tfms:
            existing_directors = set(tfm.directors.values_list("id", flat=True))
            incoming_directors = set(d.id for d in directors)
            if existing_directors == incoming_directors:
                raise serializers.ValidationError({
                    "non_field_errors": ["This TFM with same title, author, and directors already exists."]
                })

        return attrs

    def validate_directors(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("A TFM can have a maximum of 2 directors.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        provided_directors = validated_data.pop("directors", [])

        # ✅ Make sure author is assigned if given
        author = validated_data.get("author")
        # Auto assign author if not admin
        if not author and user.role == User.STUDENT:
            validated_data["author"] = user

        # Auto assign director if teacher or admin and no explicit directors
        if not provided_directors and (user.role == User.TEACHER or user.is_superuser):
            provided_directors = [user]

        tfm = TFM.objects.create(**validated_data)
        tfm.directors.set(provided_directors)

        # Status based on role
        tfm.status = "approved" if user.role in [User.TEACHER] or user.is_staff else "pending"
        tfm.save()
        return tfm


class TFMReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    directors = UserSerializer(many=True)
    review = TFMReviewSerializer(read_only=True)
    semester = serializers.SerializerMethodField()

    class Meta:
        model = TFM
        fields = [
            'id', 'title', 'description', 'file', 'attachment',
            'created_at', 'status', 'author', 'directors', 'review', 'semester',
        ]

    def get_semester(self, obj):
        # Try to get semester from related objects
        try:
            semester = obj.tribunal.slot.track.semester
            if semester:
                return str(semester)
        except AttributeError:
            pass
        # If not assigned, return current semester by created_at
        created = obj.created_at.date() if obj.created_at else timezone.now().date()
        current = Semester.objects.filter(start_date__lte=created, end_date__gte=created).first()
        return str(current) if current else None
