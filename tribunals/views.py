import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions
from .models import Tribunal
from .serializers import TribunalSerializer, TribunalReadSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from judges.serializers import AssignJudgeRoleSerializer
from judges.models import Judge

class TribunalFilter(django_filters.FilterSet):
    slot__track__semester = django_filters.NumberFilter(field_name="slot__track__semester")

    class Meta:
        model = Tribunal
        fields = ["slot__track__semester"]

class TribunalViewSet(viewsets.ModelViewSet):
    queryset = Tribunal.objects.all()
    filter_backends = [DjangoFilterBackend]  # Enable filtering
    filterset_class = TribunalFilter  # Enable ?slot__track__semester=X

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'available', 'ready']:
            return TribunalReadSerializer
        return TribunalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available', 'ready']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Returns tribunals that are NOT full.
        """
        tribunals = Tribunal.objects.all()
        not_full = [tribunal for tribunal in tribunals if not tribunal.is_full()]
        serializer = self.get_serializer(not_full, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ready(self, request):
        """
        Returns tribunals that are ready (>=3 judges).
        """
        tribunals = Tribunal.objects.all()
        ready = [tribunal for tribunal in tribunals if tribunal.is_ready()]
        serializer = self.get_serializer(ready, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def auto_assign(self, request, pk=None):
        tribunal = self.get_object()
        user = request.user
        role = request.data.get("role")

        if role not in ['president', 'secretary', 'vocal']:
            return Response({"detail": "Invalid role."}, status=400)

        serializer = AssignJudgeRoleSerializer(data={
            "tribunal": tribunal.id,
            "user": user.id,
            "role": role
        })

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": f"You have been assigned as {role}."})
        else:
            return Response(serializer.errors, status=400)
