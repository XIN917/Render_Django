from rest_framework import serializers
from .models import TFM, Director, TFMReview
from django.contrib.auth import get_user_model

User = get_user_model()

class TFMReviewSerializer(serializers.ModelSerializer):
    reviewed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = TFMReview
        fields = ['reviewed_at', 'reviewed_by', 'action', 'comment']


class TFMSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
    )
    directors = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Director.objects.all(),
        required=False
    )
    review = TFMReviewSerializer(read_only=True)

    class Meta:
        model = TFM
        fields = [
            'id', 'title', 'description', 'file',
            'created_at', 'status',
            'student', 'directors',
            'review',
        ]
        read_only_fields = ['status', 'created_at', 'review']

    def create(self, validated_data):
        user = self.context['request'].user

        if user.role == User.STUDENT:
            validated_data['student'] = user
            validated_data['status'] = 'pending'

        elif user.role == User.TEACHER:
            try:
                director = Director.objects.get(user=user)
            except Director.DoesNotExist:
                raise serializers.ValidationError("You're a teacher, but not registered as a Director.")
            validated_data.setdefault('directors', [])
            validated_data['directors'].append(director)
            validated_data['status'] = 'approved'

        elif user.is_staff or user.is_superuser:
            validated_data['status'] = 'approved'

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        forbidden_fields = {'student', 'directors'}

        if user.role in [User.STUDENT, User.TEACHER]:
            for field in forbidden_fields:
                if field in validated_data:
                    raise serializers.ValidationError({field: "You are not allowed to modify this field."})

        return super().update(instance, validated_data)
