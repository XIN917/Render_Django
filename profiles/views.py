from .models import Profile
from rest_framework import generics, permissions, viewsets
from .serializers import ProfileReadSerializer, ProfileSerializer
from rest_framework.permissions import IsAdminUser

class MyProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return ProfileReadSerializer
        return ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProfileReadSerializer
        return ProfileSerializer