from rest_framework import viewsets, permissions
from .models import Track
from .serializers import TrackSerializer, TrackReadSerializer

class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TrackReadSerializer
        return TrackSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
