from rest_framework import viewsets, permissions
from .models import Tribunal, TribunalMember
from .serializers import TribunalSerializer, TribunalReadSerializer, AssignTribunalRoleSerializer

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

class TribunalMemberViewSet(viewsets.ModelViewSet):
    queryset = TribunalMember.objects.all()
    serializer_class = AssignTribunalRoleSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
