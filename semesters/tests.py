from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Semester

User = get_user_model()

class SemesterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.semester = Semester.objects.create(
            name="Spring 2025",
            start_date="2025-01-10",
            end_date="2025-05-10",
            int_presentation_date="2025-05-19",
            last_presentation_date="2025-05-23",
            min_committees=3,
            max_committees=5
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            full_name="Admin",
            password="adminpass"
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            full_name="User",
            password="userpass"
        )

    # ─────────────────────────────────────────
    # 📁 Model
    # ─────────────────────────────────────────
    def test_str_method(self):
        self.assertEqual(str(self.semester), "Spring 2025")

    # ─────────────────────────────────────────
    # 📁 View Permissions + Endpoints
    # ─────────────────────────────────────────
    def test_list_semesters_is_public(self):
        response = self.client.get("/semesters/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_semester_is_public(self):
        response = self.client.get(f"/semesters/{self.semester.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Spring 2025")

    def test_create_semester_requires_admin(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/semesters/", {
            "name": "Fall 2025",
            "start_date": "2025-08-01",
            "end_date": "2025-12-10",
            "int_presentation_date": "2025-12-19",
            "last_presentation_date": "2025-12-23",
            "min_committees": 3,
            "max_committees": 5
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_semester(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/semesters/", {
            "name": "Fall 2025",
            "start_date": "2025-08-01",
            "end_date": "2025-12-10",
            "int_presentation_date": "2025-12-19",
            "last_presentation_date": "2025-12-23",
            "min_committees": 3,
            "max_committees": 5
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
