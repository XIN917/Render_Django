from rest_framework import viewsets, permissions
from .models import Judge
from .serializers import JudgeSerializer, AssignJudgeRoleSerializer

class JudgeViewSet(viewsets.ModelViewSet):
    queryset = Judge.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return JudgeSerializer
        return AssignJudgeRoleSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
