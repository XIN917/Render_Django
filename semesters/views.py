from rest_framework import viewsets, permissions
from .models import Semester
from .serializers import SemesterSerializer
from users.permissions import IsAdmin
from rest_framework.response import Response

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdmin()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            # Handle ProtectedError or any other deletion error
            if hasattr(e, 'protected_objects') or 'protected' in str(type(e)).lower():
                return Response(
                    {"detail": "Cannot delete semester: tracks are still associated with this semester."},
                    status=400
                )
            raise
