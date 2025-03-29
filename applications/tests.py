from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import TeacherApplication
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ApplicationPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.admin = User.objects.create_user(
            email="admin@example.com",
            full_name="Admin User",
            password="adminpass",
            role=User.TEACHER,
            is_staff=True
        )

        self.student = User.objects.create_user(
            email="student@example.com",
            full_name="Student User",
            password="studentpass",
            role=User.STUDENT
        )

        # Create a teacher application for the student
        self.application = TeacherApplication.objects.create(
            user=self.student,
            certificate=SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf"),
            additional_info="Some info"
        )

    def test_student_can_see_own_application(self):
        """Test student can view their own application"""
        self.client.force_login(self.student)
        response = self.client.get(f"/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["id"], self.student.id)

    def test_student_cannot_delete_non_pending_application(self):
        """Test student cannot delete application that isn't pending"""
        self.application.status = TeacherApplication.APPROVED
        self.application.save()

        self.client.force_login(self.student)
        response = self.client.delete(f"/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_can_delete_pending_application(self):
        """Test student can delete a pending application"""
        self.application.status = TeacherApplication.PENDING
        self.application.save()

        self.client.force_login(self.student)
        response = self.client.delete(f"/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_student_cannot_submit_application_when_pending(self):
        """Test student cannot submit a new application if one is already pending"""
        self.client.force_login(self.student)
        response = self.client.post("/applications/submit/", {
            "certificate": SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf"),
            "additional_info": "Some info"
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already have a pending application", str(response.data))

    def test_admin_can_approve_or_reject_application(self):
        """Test admin can approve or reject applications"""
        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "status": TeacherApplication.APPROVED
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, TeacherApplication.APPROVED)

    def test_admin_cannot_reapprove_application(self):
        """Test admin cannot approve/reject an already processed application"""
        self.application.status = TeacherApplication.APPROVED
        self.application.save()

        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "status": TeacherApplication.REJECTED
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This application has already been processed", str(response.data))

    def test_admin_can_view_all_applications(self):
        """Test admin can view all applications"""
        self.client.force_login(self.admin)
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_student_cannot_view_all_applications(self):
        """Test student cannot view all applications"""
        self.client.force_login(self.student)
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_create_application(self):
        """Test admin cannot submit an application"""
        self.client.force_login(self.admin)
        response = self.client.post("/applications/submit/", {
            "certificate": SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf"),
            "additional_info": "Some info"
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Admin should not be allowed
