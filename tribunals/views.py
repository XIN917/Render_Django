from rest_framework import viewsets, permissions
from .models import Tribunal, Judge
from .serializers import TribunalSerializer, TribunalReadSerializer


class TribunalViewSet(viewsets.ModelViewSet):
    queryset = Tribunal.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TribunalReadSerializer
        return TribunalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

