from rest_framework import viewsets, permissions
from .models import Semester
from .serializers import SemesterSerializer
from users.permissions import IsAdmin

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdmin()]
