from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from tfms.models import TFM, Director
from django.core.files.uploadedfile import SimpleUploadedFile

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
            role=User.TEACHER
        )
        self.student = User.objects.create_user(
            email="student@test.com",
            full_name="Student User",
            password="studpass",
            role=User.STUDENT
        )

        # Create a Director object for teacher
        self.director = Director.objects.create(user=self.teacher)

        # Create a TFM assigned to the student and teacher
        self.tfm = TFM.objects.create(
            title="Initial TFM",
            description="Test description",
            file="tfms/test.pdf",
            student=self.student,
            status="pending"
        )
        self.tfm.directors.add(self.director)

    def test_student_upload(self):
        self.client.force_login(self.student)
        dummy_file = SimpleUploadedFile("test.pdf", b"dummy content", content_type="application/pdf")

        response = self.client.post("/tfms/upload/", {
            "title": "New TFM",
            "description": "A test submission",
            "file": dummy_file,
            "directors": [self.director.id]
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_teacher_create(self):
        self.client.force_login(self.teacher)
        dummy_file = SimpleUploadedFile("created_by_teacher.pdf", b"dummy", content_type="application/pdf")

        response = self.client.post("/tfms/create/", {
            "title": "Teacher TFM",
            "description": "By the teacher",
            "file": dummy_file,
            "student": self.student.id,
            "directors": [self.director.id]
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_see_all(self):
        self.client.force_login(self.admin)
        response = self.client.get("/tfms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_student_cannot_review(self):
        self.client.force_login(self.student)
        response = self.client.post(f"/tfms/review/{self.tfm.id}/", {
            "action": "approved",
            "comment": "Should not be allowed"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_director_can_review(self):
        self.client.force_login(self.teacher)
        response = self.client.post(f"/tfms/review/{self.tfm.id}/", {
            "action": "approved",
            "comment": "Looks good"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
