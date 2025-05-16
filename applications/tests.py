from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import TeacherApplication
from institutions.models import Institution

User = get_user_model()

class ApplicationPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.institution = Institution.objects.create(name="UAB", city="Cerdanyola del Vallès")

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

        self.application = TeacherApplication.objects.create(
            user=self.student,
            institution=self.institution,
            attachment=SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")
        )

    # ─────────────────────────────────────────
    # 📁 Student: View and Delete Application
    # ─────────────────────────────────────────
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

    def test_my_application_not_found(self):
        self.application.delete()
        self.client.force_login(self.student)
        response = self.client.get("/applications/my/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ─────────────────────────────────────────
    # 📁 Student: Submit Application
    # ─────────────────────────────────────────
    def test_student_cannot_submit_application_when_pending(self):
        self.client.force_login(self.student)
        response = self.client.post("/applications/submit/", {
            "institution": self.institution.id,
            "attachment": SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You already have a pending application", str(response.data))

    def test_submit_application_with_non_pdf_attachment(self):
        self.application.delete()
        self.client.force_login(self.student)
        response = self.client.post("/applications/submit/", {
            "institution": self.institution.id,
            "attachment": SimpleUploadedFile("invalid.txt", b"not a pdf", content_type="text/plain")
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only PDF attachments", str(response.data))

    def test_submit_application_without_institution(self):
        self.application.delete()
        self.client.force_login(self.student)
        response = self.client.post("/applications/submit/", {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Institution is required", str(response.data))

    # ─────────────────────────────────────────
    # 📁 Admin: Manage Applications
    # ─────────────────────────────────────────
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

    def test_admin_updates_attachment_and_institution_only(self):
        new_attachment = SimpleUploadedFile("new.pdf", b"updated content", content_type="application/pdf")
        new_institution = Institution.objects.create(name="New Uni", city="Barcelona")
        self.application.status = TeacherApplication.PENDING
        self.application.save()

        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "attachment": new_attachment,
            "institution": new_institution.id
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.institution.id, new_institution.id)
        self.application.refresh_from_db()
        self.assertIn("new", self.application.attachment.name)

    def test_manage_application_invalid_institution(self):
        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "status": TeacherApplication.APPROVED,
            "institution": 9999
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manage_application_non_pdf_attachment(self):
        self.application.status = TeacherApplication.PENDING
        self.application.save()
        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "status": TeacherApplication.APPROVED,
            "attachment": SimpleUploadedFile("invalid.txt", b"bad", content_type="text/plain")
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only PDF attachments", str(response.data))

    def test_manage_application_get_as_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(f"/applications/{self.application.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.application.id)

    def test_manage_application_student_get_object_not_found(self):
        self.application.delete()
        self.client.force_login(self.student)
        response = self.client.get(f"/applications/{self.student.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_without_status_only_attachment(self):
        self.application.status = TeacherApplication.PENDING
        self.application.save()

        self.client.force_login(self.admin)
        new_attachment = SimpleUploadedFile("doc.pdf", b"file", content_type="application/pdf")
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "attachment": new_attachment
        }, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertIn("doc", self.application.attachment.name)

    def test_update_without_status_only_institution(self):
        self.application.status = TeacherApplication.PENDING
        self.application.save()
        new_inst = Institution.objects.create(name="UPC", city="Terrassa")

        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {
            "institution": new_inst.id
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.institution.id, new_inst.id)

    def test_update_with_nothing_still_succeeds(self):
        self.application.status = TeacherApplication.PENDING
        self.application.save()

        self.client.force_login(self.admin)
        response = self.client.patch(f"/applications/{self.application.id}/", {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ─────────────────────────────────────────
    # 📁 View: List Applications
    # ─────────────────────────────────────────
    def test_admin_can_view_all_applications(self):
        self.client.force_login(self.admin)
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_applications_denied_for_student(self):
        self.client.force_login(self.student)
        response = self.client.get("/applications/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ─────────────────────────────────────────
    # 📁 Admin Permissions
    # ─────────────────────────────────────────
    def test_admin_cannot_create_application(self):
        self.client.force_login(self.admin)
        response = self.client.post("/applications/submit/", {
            "institution": self.institution.id,
            "attachment": SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ─────────────────────────────────────────
    # 📁 Model Method Tests
    # ─────────────────────────────────────────
    def test_clean_rejects_non_pdf(self):
        app = TeacherApplication(
            user=self.student,
            institution=self.institution,
            attachment=SimpleUploadedFile("test.txt", b"dummy", content_type="text/plain")
        )
        with self.assertRaises(ValidationError):
            app.clean()
    
    def test_clean_allows_pdf(self):
        app = TeacherApplication(
            user=self.student,
            institution=self.institution,
            attachment=SimpleUploadedFile("valid.pdf", b"dummy", content_type="application/pdf")
        )
        # Should not raise
        app.clean()

    def test_approve_sets_role_and_institution(self):
        app = TeacherApplication.objects.create(user=self.student, institution=self.institution, status=TeacherApplication.PENDING)
        app.approve()
        self.assertEqual(app.status, TeacherApplication.APPROVED)
        self.assertEqual(app.user.role, "teacher")
        app.user.refresh_from_db()
        self.assertEqual(app.user.profile.institution_id, self.institution.id)

    def test_reject_sets_status(self):
        app = TeacherApplication.objects.create(user=self.student, institution=self.institution, status=TeacherApplication.PENDING)
        app.reject()
        self.assertEqual(app.status, TeacherApplication.REJECTED)

    def test_cannot_reject_non_pending(self):
        app = TeacherApplication.objects.create(user=self.student, institution=self.institution, status=TeacherApplication.APPROVED)
        with self.assertRaises(ValidationError):
            app.reject()

    def test_cannot_approve_non_pending(self):
        app = TeacherApplication.objects.create(user=self.student, institution=self.institution, status=TeacherApplication.REJECTED)
        with self.assertRaises(ValidationError):
            app.approve()

    def test_str_method(self):
        self.assertIn(self.student.email, str(self.application))
