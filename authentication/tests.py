from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from authentication.serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="student@example.com",
            full_name="Student",
            password="secure123",
            role="student"
        )
        self.url_login = reverse('login')
        self.url_register = reverse('register')
        self.url_set_password = reverse('set_password')
        self.url_reset_password = reverse('reset_password')

    # ─────────────────────────────────────────
    # 🔐 Register
    # ─────────────────────────────────────────
    def test_register_sets_student_role(self):
        response = self.client.post(self.url_register, {
            "email": "new@example.com",
            "full_name": "New User",
            "password": "newpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email="new@example.com").role, "student")

    # ─────────────────────────────────────────
    # 🔐 Login
    # ─────────────────────────────────────────
    def test_login_success(self):
        response = self.client.post(self.url_login, {
            "email": self.user.email,
            "password": "secure123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["role"], self.user.role)

    def test_login_wrong_email(self):
        response = self.client.post(self.url_login, {
            "email": "notfound@example.com",
            "password": "whatever"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("User with this email does not exist", str(response.data))

    def test_login_wrong_password(self):
        response = self.client.post(self.url_login, {
            "email": self.user.email,
            "password": "wrongpass"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("Incorrect password", str(response.data))

    # ─────────────────────────────────────────
    # 🔐 Set Password
    # ─────────────────────────────────────────
    def test_set_password_for_user_with_no_password(self):
        user = User.objects.create(email="nopass@example.com", full_name="No Pass")
        response = self.client.post(self.url_set_password, {
            "email": user.email,
            "password": "newsetpass"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password("newsetpass"))

    def test_set_password_user_not_found(self):
        response = self.client.post(self.url_set_password, {
            "email": "ghost@example.com",
            "password": "nopass"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("User not found", str(response.data))

    def test_set_password_already_exists(self):
        response = self.client.post(self.url_set_password, {
            "email": self.user.email,
            "password": "newpass"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already have a password", str(response.data))

    # ─────────────────────────────────────────
    # 🔐 Reset Password
    # ─────────────────────────────────────────
    def test_reset_password_success(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url_reset_password, {
            "old_password": "secure123",
            "new_password": "newsecure123",
            "confirm_password": "newsecure123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecure123"))

    def test_reset_password_wrong_old(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url_reset_password, {
            "old_password": "wrongold",
            "new_password": "newpass",
            "confirm_password": "newpass"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_reset_password_mismatch(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url_reset_password, {
            "old_password": "secure123",
            "new_password": "abc123",
            "confirm_password": "xyz456"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords do not match", str(response.data))

    def test_reset_password_same_as_old(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(self.url_reset_password, {
            "old_password": "secure123",
            "new_password": "secure123",
            "confirm_password": "secure123"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cannot be the same as the old", str(response.data))
