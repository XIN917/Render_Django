from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from .models import Slot
from .serializers import SlotSerializer, SlotReadSerializer

class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['track__semester']  # Enables ?track__semester=ID

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SlotReadSerializer
        return SlotSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
