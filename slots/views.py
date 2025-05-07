from django_filters import rest_framework as filters
from rest_framework import viewsets, permissions
from .models import Slot
from .serializers import SlotSerializer, SlotReadSerializer

class SlotFilter(filters.FilterSet):
    semester = filters.CharFilter(field_name="track__semester__id", lookup_expr="exact")

    class Meta:
        model = Slot
        fields = ['semester']

class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SlotFilter  # Use the custom filter class

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SlotReadSerializer
        return SlotSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]