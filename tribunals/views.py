from rest_framework import viewsets, permissions
from .models import Tribunal
from .serializers import TribunalSerializer

class TribunalViewSet(viewsets.ModelViewSet):
    queryset = Tribunal.objects.all()
    serializer_class = TribunalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]