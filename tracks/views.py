from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from .models import Track
from .serializers import TrackSerializer, TrackReadSerializer
from rest_framework.response import Response
from django.db.models.deletion import ProtectedError
from rest_framework.decorators import action

class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['semester']  # enable ?semester=ID filtering

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'ready']:
            return TrackReadSerializer
        return TrackSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'ready']:
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

    @action(detail=False, methods=['get'])
    def ready(self, request):
        """
        Returns tracks that have at least one ready tribunal (tribunal with at least one president, one secretary, and one vocal).
        Optional: filter by semester (?semester=ID).
        """
        semester = request.query_params.get("semester")
        from tribunals.models import Tribunal
        tracks = self.queryset
        if semester:
            tracks = tracks.filter(semester=semester)
        # Only include tracks with at least one ready tribunal (using new is_ready logic)
        ready_track_ids = set(
            t.slot.track_id for t in Tribunal.objects.filter(slot__track__in=tracks)
            if t.is_ready()
        )
        ready_tracks = tracks.filter(id__in=ready_track_ids)
        serializer = self.get_serializer(ready_tracks, many=True)
        return Response(serializer.data)