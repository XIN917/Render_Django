from django_filters import rest_framework as filters
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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

    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        # Get current semester (latest by start_date <= today <= end_date)
        from datetime import date
        from semesters.models import Semester
        today = date.today()
        current_semester = Semester.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-start_date').first()
        if not current_semester:
            return Response([], status=200)
        available_slots = [slot for slot in self.get_queryset().filter(track__semester=current_semester) if not slot.is_full()]
        serializer = SlotReadSerializer(available_slots, many=True)
        return Response(serializer.data)