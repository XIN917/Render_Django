from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .models import TFM, TFMReview
from .serializers import TFMSerializer, TFMReadSerializer
from users.permissions import IsStudent, IsTeacher, IsAdmin, IsAdminOrTeacher

User = get_user_model()


# 🧑‍🎓 Student uploads their own TFM
class StudentUploadTFMView(generics.CreateAPIView):
    serializer_class = TFMSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]


# 👨‍🏫 Admin or teacher creates a TFM (auto-approved)
class AdminOrTeacherCreateTFMView(generics.CreateAPIView):
    serializer_class = TFMSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacher]


# 🔐 Admin-only view: list all TFMs
class AllTFMsAdminView(generics.ListAPIView):
    serializer_class = TFMReadSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return TFM.objects.all()


# 📃 Each user sees their associated TFMs
class MyTFMsView(generics.ListAPIView):
    serializer_class = TFMReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.STUDENT:
            return TFM.objects.filter(student=user)
        elif user.role == User.TEACHER:
            return TFM.objects.filter(directors=user).distinct()
        elif user.is_staff or user.is_superuser:
            return TFM.objects.all()
        return TFM.objects.none()


# 🔍 View and update a specific TFM (based on role and relation)
class TFMDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TFM.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TFMReadSerializer
        return TFMSerializer

    def get_object(self):
        tfm = super().get_object()
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return tfm
        if user.role == User.STUDENT and tfm.student == user:
            return tfm
        if user.role == User.TEACHER and tfm.directors.filter(id=user.id).exists():
            return tfm

        raise PermissionDenied("You don't have permission to access this TFM.")

    def patch(self, request, *args, **kwargs):
        tfm = self.get_object()
        user = request.user

        if user.role == User.STUDENT and tfm.status != 'pending':
            raise PermissionDenied("You can only update your TFM while it's pending.")

        return super().patch(request, *args, **kwargs)


# 📝 Teachers (if director) or admins can review TFMs
class ReviewTFMView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrTeacher]

    def post(self, request, pk):
        user = request.user
        tfm = TFM.objects.filter(pk=pk).first()
        if not tfm:
            return Response({'detail': 'TFM not found.'}, status=404)

        if user.role == User.TEACHER and not tfm.directors.filter(id=user.id).exists():
            return Response({'detail': 'You are not a director of this TFM.'}, status=403)

        if tfm.status != 'pending':
            return Response({'detail': 'TFM has already been reviewed.'}, status=400)

        action = request.data.get('action')
        comment = request.data.get('comment', '')

        if action not in ['approved', 'rejected']:
            return Response({'detail': 'Invalid action. Must be "approved" or "rejected".'}, status=400)

        tfm.status = action
        tfm.save()

        TFMReview.objects.create(
            tfm=tfm,
            reviewed_by=user,
            action=action,
            comment=comment,
        )

        return Response({
            'detail': f'TFM has been {action}.',
            'status': action,
            'tfm_id': tfm.id,
        }, status=200)
