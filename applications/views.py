from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
from .models import TeacherApplication
from .serializers import TASerializer, TAUpdateSerializer
from users.permissions import IsStudent, IsAdmin

User = get_user_model()


# 🟢 Student retrieves or deletes their current application
class MyApplicationView(generics.RetrieveDestroyAPIView):
    serializer_class = TASerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_object(self):
        # Ensure the student has an application
        application = TeacherApplication.objects.filter(user=self.request.user).order_by('-created_at').first()
        if not application:
            raise NotFound("You don't have any application yet.")
        return application

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        # Only allow deletion if the application is pending
        if instance.status != TeacherApplication.PENDING:
            raise ValidationError("You can only delete a pending application.")
        
        instance.delete()
        return Response({"detail": "Your application has been deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# 🟢 Student submits a teacher application
class SubmitApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request):
        user = request.user

        # Check if the student already has a pending application
        if TeacherApplication.objects.filter(user=user, status=TeacherApplication.PENDING).exists():
            return Response({"error": "You already have a pending application"}, status=400)

        # Validate certificate and additional info
        certificate = request.FILES.get('certificate')
        if not certificate or not certificate.name.lower().endswith('.pdf'):
            return Response({"error": "A valid PDF certificate is required"}, status=400)

        additional_info = request.data.get('additional_info', '')

        # Create the application
        application = TeacherApplication.objects.create(
            user=user,
            certificate=certificate,
            additional_info=additional_info
        )

        return Response(TASerializer(application).data, status=status.HTTP_201_CREATED)


# 🟡 Admin approves/rejects applications
class ManageTApplicationView(generics.RetrieveUpdateAPIView):
    queryset = TeacherApplication.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        return TASerializer if self.request.method == 'GET' else TAUpdateSerializer

    def get_object(self):
        user = self.request.user

        # Admins can manage all applications
        if user.is_staff:
            return super().get_object()

        # Students can only access their own applications
        application = TeacherApplication.objects.filter(user=user).order_by('-created_at').first()
        if not application:
            raise NotFound("You don't have any application yet.")
        return application

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Prevent re-approval or re-rejection
        if instance.status != TeacherApplication.PENDING:
            return Response({"error": "This application has already been processed"}, status=400)

        # Validate and perform the update
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=200)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()

        # Admins can delete any application
        if request.user.is_staff or instance.status == TeacherApplication.PENDING:
            instance.delete()
            return Response({"detail": "Application deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        raise ValidationError("You can only delete a pending application.")


# 🔵 List teacher applications (students see pending, Admins see all)
class ListApplicationsView(generics.ListAPIView):
    serializer_class = TASerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admins can view all applications
        if user.is_staff:
            return TeacherApplication.objects.all()

        # Students cannot view any applications (even their own)
        raise PermissionDenied("You do not have permission to view applications.")
