from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from .models import TFM, TFMReview
from .serializers import TFMSerializer, TFMReadSerializer
from users.permissions import IsStudent, IsTeacher, IsAdmin, IsAdminOrTeacher

User = get_user_model()


class TFMFilter(django_filters.FilterSet):
    semester = django_filters.CharFilter(field_name="tribunal__slot__track__semester__id")

    class Meta:
        model = TFM
        fields = ['semester']


class TFMViewSet(viewsets.ModelViewSet):
    queryset = TFM.objects.all()
    serializer_class = TFMSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TFMFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list', 'my_tfms', 'pending_tfms', 'available_tfms']:
            return TFMReadSerializer
        return TFMSerializer

    def get_permissions(self):
        if self.action == 'create':
            if self.request.user.role == User.STUDENT:
                permission_classes = [permissions.IsAuthenticated, IsStudent]
            else:
                permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacher]
        elif self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        elif self.action in ['my_tfms', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'review':
            permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [perm() for perm in permission_classes]

    def get_queryset(self):
        if self.action == 'my_tfms':
            user = self.request.user
            if user.role == User.STUDENT:
                return TFM.objects.filter(author=user)
            elif user.role == User.TEACHER:
                return TFM.objects.filter(directors=user).distinct()
            elif user.is_staff or user.is_superuser:
                return TFM.objects.all()
            return TFM.objects.none()
        return super().get_queryset()

    def perform_update(self, serializer):
        tfm = self.get_object()
        user = self.request.user
        if user.role == User.STUDENT and tfm.status != 'pending':
            raise PermissionDenied("You can only update your TFM while it's pending.")
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        tfm = self.get_object()
        user = request.user
        if user.is_staff or user.is_superuser or \
           (user.role == User.STUDENT and tfm.author == user) or \
           (user.role == User.TEACHER and tfm.directors.filter(id=user.id).exists()):
            return super().retrieve(request, *args, **kwargs)
        raise PermissionDenied("You don't have permission to access this TFM.")

    @action(detail=False, methods=['get'], url_path='my')
    def my_tfms(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='review')
    def review(self, request, pk=None):
        tfm = self.get_object()
        user = request.user

        if user.role == User.TEACHER and not (user.is_staff or user.is_superuser):
            if not tfm.directors.filter(id=user.id).exists():
                return Response({'detail': 'You are not a director of this TFM.'}, status=403)

        if tfm.status != 'pending':
            return Response({'detail': 'TFM has already been reviewed.'}, status=400)

        action = request.data.get('action')
        comment = request.data.get('comment', '')

        if action not in ['approved', 'rejected']:
            return Response({'detail': 'Invalid action. Must be "approved" or "rejected".'}, status=400)

        tfm.status = action
        tfm.save()

        TFMReview.objects.create(
            tfm=tfm,
            reviewed_by=user,
            action=action,
            comment=comment,
        )

        return Response({
            'detail': f'TFM has been {action}.',
            'status': action,
            'tfm_id': tfm.id,
        }, status=200)
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_tfms(self, request):
        if not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied("Only admins can access pending TFMs.")

        pending = TFM.objects.filter(status='pending')
        page = self.paginate_queryset(pending)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='available')
    def available_tfms(self, request):
        if not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied("Only admins can access available TFMs.")

        available = TFM.objects.filter(status='approved', tribunal__isnull=True)
        page = self.paginate_queryset(available)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)

    '''def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Cannot delete TFM: it is still referenced by a Tribunal."},
                status=400
            )'''
