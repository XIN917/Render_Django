from rest_framework import viewsets, permissions
from .models import Institution
from .serializers import InstitutionSerializer

class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all().order_by('name')
    serializer_class = InstitutionSerializer

    # Optional: restrict modifications to staff/admin only
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
