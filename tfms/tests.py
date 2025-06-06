from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

from tfms.models import TFM
from tribunals.models import Tribunal
from slots.models import Slot
from tracks.models import Track
from semesters.models import Semester
from datetime import time, timedelta, date

User = get_user_model()

class TFMTestCase(APITestCase):

    def tearDown(self):
        for tfm in TFM.objects.all():
            if tfm.file:
                tfm.file.delete(save=False)

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@test.com", full_name="Admin User", password="adminpass",
            role=User.TEACHER, is_staff=True
        )
        self.teacher = User.objects.create_user(
            email="teacher@test.com", full_name="Teacher User", password="teachpass",
            role=User.TEACHER
        )
        self.student = User.objects.create_user(
            email="student@test.com", full_name="Student User", password="studpass",
            role=User.STUDENT
        )

        self.tfm = TFM.objects.create(
            title="Initial TFM",
            description="Test description",
            file=SimpleUploadedFile("test.pdf", b"Initial content", content_type="application/pdf"),
            author=self.student,
            status="pending"
        )
        self.tfm.directors.add(self.teacher)

        # Required objects for available TFMs test
        self.available_tfm = TFM.objects.create(
            title="Available TFM",
            description="Approved and no tribunal",
            file=SimpleUploadedFile("available.pdf", b"Approved Content"),
            author=self.student,
            status="approved"
        )
        self.available_tfm.directors.add(self.teacher)

        self.linked_tfm = TFM.objects.create(
            title="Linked TFM",
            description="Approved but with tribunal",
            file=SimpleUploadedFile("linked.pdf", b"Linked Content"),
            author=self.student,
            status="approved"
        )
        self.linked_tfm.directors.add(self.teacher)

        self.semester = Semester.objects.create(
            name="Spring 2025", start_date=date(2025, 2, 1), end_date=date(2025, 6, 30),
            int_presentation_date=date(2025, 6, 15), last_presentation_date=date(2025, 6, 20),
            daily_start_time=time(8, 0), daily_end_time=time(18, 0),
            pre_duration=timedelta(minutes=45), min_committees=3, max_committees=5
        )

        self.track = Track.objects.create(
            title="Test Track",
            semester=self.semester
        )

        self.slot = Slot.objects.create(
            track=self.track, start_time=time(9, 0), end_time=time(10, 30),
            room="A101", date=date(2025, 6, 17), max_tfms=2
        )

        Tribunal.objects.create(
            tfm=self.linked_tfm,
            slot=self.slot
        )

    def test_student_upload(self):
        self.client.force_authenticate(user=self.student)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            pdf_file.write(b"Dummy content")
            pdf_file.seek(0)
            data = {
                "title": "TFM Test Student",
                "description": "TFM uploaded by student",
                "file": pdf_file,
                "directors": [self.teacher.id],
            }
            response = self.client.post("/tfms/", data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_create(self):
        self.client.force_authenticate(user=self.teacher)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            pdf_file.write(b"Dummy content")
            pdf_file.seek(0)
            data = {
                "title": "TFM Test Teacher",
                "description": "TFM created by teacher",
                "file": pdf_file,
                "author": self.student.id,
            }
            response = self.client.post("/tfms/", data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_see_all(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/tfms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_student_cannot_review(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "approved", "comment": "Should not be allowed"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_can_review(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "approved", "comment": "Looks good"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_can_review(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "approved", "comment": "Approved by admin"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tfm.refresh_from_db()
        self.assertEqual(self.tfm.status, "approved")
        self.assertEqual(self.tfm.review.reviewed_by, self.admin)

    def test_admin_create_with_all_required_fields(self):
        self.client.force_authenticate(user=self.admin)
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            pdf_file.write(b"Dummy content")
            pdf_file.seek(0)
            data = {
                "title": "Valid Admin TFM",
                "description": "All required fields",
                "file": pdf_file,
                "author": self.student.id,
                "directors": [self.teacher.id],
            }
            response = self.client.post("/tfms/", data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tfm_str(self):
        self.assertEqual(str(self.tfm), "Initial TFM")

    def test_review_str(self):
        self.client.force_authenticate(user=self.teacher)
        self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "approved", "comment": "Reviewed"
        })
        review = self.tfm.review
        expected_str = f"Review of {self.tfm.title} by {self.teacher}"
        self.assertEqual(str(review), expected_str)

    def test_max_directors_validation(self):
        self.client.force_authenticate(user=self.admin)
        extra_teacher = User.objects.create_user(
            email="extra@test.com", full_name="Extra", password="123", role=User.TEACHER
        )
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
            pdf_file.write(b"Content")
            pdf_file.seek(0)
            data = {
                "title": "Too many directors",
                "description": "Invalid",
                "file": pdf_file,
                "author": self.student.id,
                "directors": [self.teacher.id, extra_teacher.id, self.admin.id],
            }
            response = self.client.post("/tfms/", data, format="multipart")
            self.assertEqual(response.status_code, 400)
            self.assertIn("directors", response.data)

    def test_patch_not_allowed_if_not_pending(self):
        self.tfm.status = 'approved'
        self.tfm.save()
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(f"/tfms/{self.tfm.id}/", {"title": "Updated"})
        self.assertEqual(response.status_code, 403)

    def test_review_invalid_action(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "invalid", "comment": "Bad"
        })
        self.assertEqual(response.status_code, 400)

    def test_review_tfm_not_found(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post("/tfms/9999/review/", {
            "action": "approved", "comment": "None"
        })
        self.assertEqual(response.status_code, 404)

    def test_review_already_done(self):
        self.client.force_authenticate(user=self.teacher)
        self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "approved", "comment": "Looks good"
        })
        response = self.client.post(f"/tfms/{self.tfm.id}/review/", {
            "action": "approved", "comment": "Again"
        })
        self.assertEqual(response.status_code, 400)
    
    def test_pending_tfms(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/tfms/pending/")
        self.assertEqual(response.status_code, 200)

        titles = [item["title"] for item in response.data]
        self.assertIn("Initial TFM", titles)         # from setUp, status='pending'
        self.assertNotIn("Available TFM", titles)    # status='approved'
        self.assertNotIn("Linked TFM", titles)       # status='approved'
    
    def test_pending_tfms_forbidden_for_non_admin(self):
        self.client.force_authenticate(user=self.teacher)  # Not staff
        response = self.client.get("/tfms/pending/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_available_tfms(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/tfms/available/")
        self.assertEqual(response.status_code, 200)

        titles = [item["title"] for item in response.data]
        self.assertIn("Available TFM", titles)
        self.assertNotIn("Linked TFM", titles)
        self.assertNotIn("Initial TFM", titles)
    
    def test_available_tfms_forbidden_for_non_admin(self):
        # Mark TFM as approved and unlinked from tribunal
        self.tfm.status = "approved"
        self.tfm.save()

        self.client.force_authenticate(user=self.teacher)
        response = self.client.get("/tfms/available/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_semester_from_tribunal(self):
        # Linked TFM has a tribunal, so semester should be from the related objects
        from tfms.serializers import TFMReadSerializer
        serializer = TFMReadSerializer(instance=self.linked_tfm)
        data = serializer.data
        self.assertEqual(data['semester'], str(self.semester))

    def test_get_semester_from_created_at(self):
        # Available TFM has no tribunal, so semester should be inferred from created_at
        from tfms.serializers import TFMReadSerializer
        serializer = TFMReadSerializer(instance=self.available_tfm)
        data = serializer.data
        self.assertEqual(data['semester'], str(self.semester))

    def test_delete_tfm_blocked_by_tribunal(self):
        """Deleting a TFM referenced by a Tribunal should return a user-friendly error message."""
        self.client.force_authenticate(user=self.admin)
        # self.linked_tfm is referenced by a Tribunal in setUp
        response = self.client.delete(f"/tfms/{self.linked_tfm.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot delete", response.data.get("detail", ""))
        self.assertIn("tribunal", response.data.get("detail", "").lower())
        # Should not leak all related objects, just a summary
        self.assertLess(len(response.data.get("detail", "")), 300)

    def test_delete_tfm_not_referenced_by_tribunal(self):
        """
        Deleting a TFM not referenced by a Tribunal should succeed and remove the TFM.
        """
        self.client.force_authenticate(user=self.admin)
        # self.tfm is not referenced by any Tribunal
        response = self.client.delete(f"/tfms/{self.tfm.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(TFM.objects.filter(id=self.tfm.id).exists())

