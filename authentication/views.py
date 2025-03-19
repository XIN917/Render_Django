from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # Allow anyone to register

    def perform_create(self, serializer):
        """Ensure new users are always created as 'student'."""
        serializer.save(role="student")  # Enforce student role on creation


class CustomTokenObtainPairView(TokenObtainPairView):
    """ Custom Login View with role information """
    serializer_class = CustomTokenObtainPairSerializer

class SetPasswordView(generics.GenericAPIView):
    """
    Allow users without a password to set one.
    Users with an existing password must reset it via password reset.
    """
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password set successfully. You can now log in."}, status=status.HTTP_200_OK)

class ResetPasswordView(generics.GenericAPIView):
    """Allow authenticated users to reset their password."""
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        """Handle password reset request."""
        serializer = self.get_serializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
