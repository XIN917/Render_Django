from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from tfms.models import TFM
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

User = get_user_model()

class TFMTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            email="admin@test.com",
            full_name="Admin User",
            password="adminpass",
            role=User.TEACHER,
            is_staff=True
        )
        self.teacher = User.objects.create_user(
            email="teacher@test.com",
            full_name="Teacher User",
            password="teachpass",
            role=User.TEACHER,
        )
        self.student = User.objects.create_user(
            email="student@test.com",
            full_name="Student User",
            password="studpass",
            role=User.STUDENT
        )

        # Create a TFM
        self.tfm = TFM.objects.create(
            title="Initial TFM",
            description="Test description",
            file=SimpleUploadedFile("test.pdf", b"Initial content", content_type="application/pdf"),
            author=self.student,
            status="pending"
        )
        self.tfm.directors.add(self.teacher)  # ✅ Assign teacher as director

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
            response = self.client.post("/tfms/upload/", data, format="multipart")
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
            response = self.client.post("/tfms/create/", data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_see_all(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/tfms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_student_cannot_review(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f"/tfms/review/{self.tfm.id}/", {
            "action": "approved",
            "comment": "Should not be allowed"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_can_review(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(f"/tfms/review/{self.tfm.id}/", {
            "action": "approved",
            "comment": "Looks good"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
            response = self.client.post("/tfms/create/", data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
