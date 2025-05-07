from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
from .models import TeacherApplication
from .serializers import TASerializer, TAUpdateSerializer
from users.permissions import IsStudent, IsAdmin
from institutions.models import Institution

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
# 🟢 Student submits a teacher application
class SubmitApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request):
        user = request.user

        # Check for existing pending application
        if TeacherApplication.objects.filter(user=user, status=TeacherApplication.PENDING).exists():
            return Response({"error": "You already have a pending application"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate institution
        institution_id = request.data.get('institution')
        if not institution_id:
            return Response({"error": "Institution is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            institution = Institution.objects.get(id=institution_id)
        except Institution.DoesNotExist:
            return Response({"error": "Invalid institution ID"}, status=status.HTTP_404_NOT_FOUND)

        # Validate attachment
        attachment = request.FILES.get('attachment')
        if attachment and not attachment.name.lower().endswith('.pdf'):
            return Response({"error": "Only PDF attachments are allowed"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the application
        application = TeacherApplication.objects.create(
            user=user,
            institution=institution,
            attachment=attachment
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
            return Response({"error": "This application has already been processed"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate institution if provided
        institution_id = request.data.get('institution')
        if institution_id:
            try:
                institution = Institution.objects.get(id=institution_id)
                instance.institution = institution
            except Institution.DoesNotExist:
                return Response({"error": "Invalid institution ID"}, status=status.HTTP_404_NOT_FOUND)

        # Validate attachment if provided
        attachment = request.FILES.get('attachment')
        if attachment:
            if not attachment.name.lower().endswith('.pdf'):
                return Response({"error": "Only PDF attachments are allowed"}, status=status.HTTP_400_BAD_REQUEST)
            instance.attachment = attachment

        # Perform the update
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
