from rest_framework import viewsets, permissions
from .models import Tribunal, Judge
from .serializers import TribunalSerializer, TribunalReadSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class TribunalViewSet(viewsets.ModelViewSet):
    queryset = Tribunal.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'available', 'ready']:
            return TribunalReadSerializer
        return TribunalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available', 'ready']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Returns tribunals that are NOT full.
        """
        tribunals = Tribunal.objects.all()
        not_full = [tribunal for tribunal in tribunals if not tribunal.is_full()]
        serializer = self.get_serializer(not_full, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ready(self, request):
        """
        Returns tribunals that are ready (>=3 judges).
        """
        tribunals = Tribunal.objects.all()
        ready = [tribunal for tribunal in tribunals if tribunal.is_ready()]
        serializer = self.get_serializer(ready, many=True)
        return Response(serializer.data)

