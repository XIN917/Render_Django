from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import TeacherApplication
from .serializers import TASerializer, TAUpdateSerializer

# Get the custom User model
User = get_user_model()

### 🟢 STUDENT SUBMITS APPLICATION ###
class SubmitApplicationView(APIView):
    """
    API for students to apply to become a teacher.
    Users can only apply if they do not have a pending application.
    """
    def post(self, request):
        user = request.user

        if user.role != User.STUDENT:
            return Response({"error": "Only students can apply"}, status=400)
            
        if TeacherApplication.objects.filter(user=user, status=TeacherApplication.PENDING).exists():
            return Response({"error": "You already have a pending application"}, status=400)

        certificate = request.FILES.get('certificate')
        additional_info = request.data.get('additional_info', '')

        if not certificate or not certificate.name.lower().endswith('.pdf'):
            return Response({"error": "A valid PDF certificate is required"}, status=400)

        application = TeacherApplication.objects.create(
            user=user,
            certificate=certificate,
            additional_info=additional_info
        )

        return Response(TASerializer(application).data, status=201)


### 🟡 ADMIN APPROVES/REJECTS APPLICATION ###
class AdminManageApplicationView(generics.RetrieveUpdateAPIView):
    """
    API for admins to retrieve, approve, or reject teacher applications.
    Admins can only approve/reject once.
    """
    queryset = TeacherApplication.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TASerializer  # Detailed serializer for GET
        return TAUpdateSerializer  # Simplified serializer for PATCH

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Prevent re-approval or re-rejection
        if instance.status != TeacherApplication.PENDING:
            return Response({"error": "This application has already been processed"}, status=400)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return serializer.data
        return Response(serializer.data, status=200)


### 🔵 LIST APPLICATIONS (Students see pending, Admins see all) ###
class ListApplicationsView(generics.ListAPIView):
    """
    API for listing teacher applications.
    - Students only see their pending applications.
    - Admins see all applications.
    """
    serializer_class = TASerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TeacherApplication.objects.all()
        return TeacherApplication.objects.filter(user=user, status=TeacherApplication.PENDING)
