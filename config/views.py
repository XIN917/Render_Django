from rest_framework import generics, permissions
from .models import PresentationDay
from .serializers import PresentationDaySerializer

class PresentationDayView(generics.RetrieveAPIView):
    serializer_class = PresentationDaySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return PresentationDay.objects.first()
