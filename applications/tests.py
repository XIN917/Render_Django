from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import TeacherApplication
from institutions.models import Institution

User = get_user_model()

class ApplicationPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Institution
        self.institution = Institution.objects.create(name="UAB", city="Cerdanyola del Vallès")

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
            institution=self.institution,
            attachment=SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")
        )

    def test_student_can_see_own_application(self):
        self.client.force_login(self.student)
        response = self.client.get("/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["id"], self.student.id)

    def test_student_cannot_delete_non_pending_application(self):
        self.application.status = TeacherApplication.APPROVED
        self.application.save()

        self.client.force_login(self.student)
        response = self.client.delete("/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_can_delete_pending_application(self):
        self.application.status = TeacherApplication.PENDING
        self.application.save()

        self.client.force_login(self.student)
        response = self.client.delete("/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_student_cannot_submit_application_when_pending(self):
        self.client.force_login(self.student)
        response = self.client.post("/applications/submit/", {
            "institution": self.institution.id,
            "attachment": SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already have a pending application", str(response.data))

    def test_admin_can_approve_or_reject_application(self):
        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "status": TeacherApplication.APPROVED
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, TeacherApplication.APPROVED)

    def test_admin_cannot_reapprove_application(self):
        self.application.status = TeacherApplication.APPROVED
        self.application.save()

        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "status": TeacherApplication.REJECTED
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been processed", str(response.data))

    def test_admin_can_view_all_applications(self):
        self.client.force_login(self.admin)
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_student_cannot_view_all_applications(self):
        self.client.force_login(self.student)
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_create_application(self):
        self.client.force_login(self.admin)
        response = self.client.post("/applications/submit/", {
            "institution": self.institution.id,
            "attachment": SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
