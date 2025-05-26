from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import UserSerializer, UserCreateSerializer, UserSelfUpdateSerializer
from .permissions import IsAdmin

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsAdmin()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user

        # 🟢 Admin can view all users
        if user.is_superuser:
            return self.queryset.exclude(id=user.id)
        
        if user.is_staff:
            # 🟡 Staff can view all users, but not superusers
            return self.queryset.exclude(is_superuser=True).exclude(id=user.id)

        # 🟢 Authenticated users can view teachers/students, but not everyone
        role_filter = self.request.query_params.get('role')
        if role_filter in [User.TEACHER, User.STUDENT]:
            return self.queryset.filter(role=role_filter, is_superuser=False)

        # 🟠 Fallback to only current user
        return self.queryset.filter(id=user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_superuser:
            return Response(
                {"detail": "You cannot delete a superuser."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSelfUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSelfUpdateSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
