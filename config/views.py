from rest_framework import viewsets, permissions
from .models import PresentationDay
from .serializers import PresentationDaySerializer

class PresentationDayViewSet(viewsets.ModelViewSet):
    queryset = PresentationDay.objects.all()
    serializer_class = PresentationDaySerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]