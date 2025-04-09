from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user_with_defaults(self):
        user = User.objects.create_user(email="test@test.com", full_name="Test User")
        self.assertEqual(user.email, "test@test.com")
        self.assertTrue(user.check_password("12345678"))  # default password
        self.assertEqual(user.role, User.STUDENT)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_sets_flags_and_role(self):
        user = User.objects.create_superuser(email="admin@test.com", full_name="Admin User", password="adminpass")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.role, User.TEACHER)

    def test_email_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", full_name="Missing Email")


class UserPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Admin user
        self.admin = User.objects.create_user(
            email="admin@example.com",
            full_name="Admin",
            password="adminpass",
            role=User.TEACHER,
            is_staff=True
        )

        # Student user
        self.student = User.objects.create_user(
            email="student@example.com",
            full_name="Student",
            password="studentpass",
            role=User.STUDENT
        )

    def test_admin_can_list_users(self):
        self.client.force_login(self.admin)
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_student_can_see_own_detail(self):
        self.client.force_login(self.student)
        response = self.client.get(f"/users/{self.student.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.student.email)

    def test_admin_can_create_user(self):
        self.client.force_login(self.admin)
        response = self.client.post("/users/", {
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": User.STUDENT,
            "password": "12345678"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_user(self):
        self.client.force_login(self.student)
        response = self.client.post("/users/", {
            "email": "hacker@example.com",
            "full_name": "Hacker",
            "role": User.STUDENT,
            "password": "12345678"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_can_update_own_name(self):
        self.client.force_login(self.student)
        response = self.client.patch(f"/users/me/", {
            "full_name": "Updated Student"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.full_name, "Updated Student")
