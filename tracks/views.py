from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from .models import Track
from .serializers import TrackSerializer, TrackReadSerializer
from rest_framework.response import Response
from django.db.models.deletion import ProtectedError

class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['semester']  # enable ?semester=ID filtering

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TrackReadSerializer
        return TrackSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            return Response(
                {"detail": "Cannot delete track: slots are still associated with this track."},
                status=status.HTTP_400_BAD_REQUEST
            )