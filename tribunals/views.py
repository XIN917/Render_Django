from rest_framework import viewsets, permissions
from .models import Tribunal
from .serializers import TribunalSerializer, TribunalReadSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from committees.serializers import AssignCommitteeRoleSerializer
from committees.models import Committee
from datetime import datetime, date
from semesters.models import Semester

from django_filters import rest_framework as filters

class TribunalFilter(filters.FilterSet):
    semester = filters.CharFilter(field_name="slot__track__semester")

    class Meta:
        model = Tribunal
        fields = ["semester"]

class TribunalViewSet(viewsets.ModelViewSet):
    queryset = Tribunal.objects.all()
    filter_backends = [filters.DjangoFilterBackend]  # Enable filtering
    filterset_class = TribunalFilter  # Enable ?semester=ID

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'available', 'ready', 'my_assignments']:
            return TribunalReadSerializer
        return TribunalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available', 'ready', 'my_assignments']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def _get_user_assigned_tribunals(self, user):
        return Tribunal.objects.filter(
            committees__user=user
        ).distinct().select_related(
            'slot__track__semester', 'tfm'
        ).prefetch_related('committees__user')

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_assignments(self, request):
        user = request.user
        semester = request.query_params.get("semester")

        tribunals = self._get_user_assigned_tribunals(user)
        if semester:
            tribunals = tribunals.filter(slot__track__semester=semester)

        serializer = self.get_serializer(tribunals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def available(self, request):
        user = request.user
        assigned_tribunals = self._get_user_assigned_tribunals(user)

        user_tribunal_times = []
        for tribunal in assigned_tribunals:
            slot = tribunal.slot
            start_dt = datetime.combine(date.today(), slot.start_time) + (
                (tribunal.index - 1) * slot.track.semester.pre_duration
            )
            end_dt = start_dt + slot.track.semester.pre_duration
            user_tribunal_times.append((start_dt, end_dt))

        def no_conflict(tribunal):
            slot = tribunal.slot
            start_dt = datetime.combine(date.today(), slot.start_time) + (
                (tribunal.index - 1) * slot.track.semester.pre_duration
            )
            end_dt = start_dt + slot.track.semester.pre_duration
            return all(not (start_dt < usr_end and end_dt > usr_start) for usr_start, usr_end in user_tribunal_times)

        # Only return tribunals from the current semester
        current_semester = Semester.objects.filter(
            start_date__lte=date.today(),
            end_date__gte=date.today()
        ).first()

        if not current_semester:
            return Response([], status=200)  # Or optionally return a message

        all_tribunals = Tribunal.objects.select_related('slot__track__semester').filter(
            slot__track__semester=current_semester
        )

        available_tribunals = [
            tribunal for tribunal in all_tribunals
            if not tribunal.is_full() and no_conflict(tribunal)
        ]

        serializer = self.get_serializer(available_tribunals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ready(self, request):
        """
        Returns tribunals that are ready (>=3 committees), optionally filtered by semester.
        """
        semester = request.query_params.get("semester")
        tribunals = Tribunal.objects.select_related("slot__track__semester").all()

        if semester:
            tribunals = tribunals.filter(slot__track__semester=semester)

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

        serializer = AssignCommitteeRoleSerializer(data={
            "tribunal": tribunal.id,
            "user": user.id,
            "role": role
        })

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": f"You have been assigned as {role}."})
        else:
            return Response(serializer.errors, status=400)
