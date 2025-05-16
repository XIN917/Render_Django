from rest_framework import viewsets, permissions
from .models import Committee
from .serializers import CommitteeSerializer, AssignCommitteeRoleSerializer

class CommitteeViewSet(viewsets.ModelViewSet):
    queryset = Committee.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CommitteeSerializer
        return AssignCommitteeRoleSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
