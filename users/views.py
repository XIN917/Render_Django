from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    - `GET /users/` → List all users (Admin only)
    - `POST /users/` → Create a new user (Admin only)
    - `GET /users/<id>/` → Retrieve a user (Admin or self)
    - `PUT/PATCH /users/<id>/` → Update a user (Admin or self)
    - `DELETE /users/<id>/` → Delete a user (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers for creating users."""
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """Admins can see all users, regular users can only see themselves."""
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)

class CurrentUserView(APIView):
    """Retrieve details of the currently authenticated user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)