from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from institutions.models import Institution
from .models import Profile

User = get_user_model()

class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.institution = Institution.objects.create(name="UPC", city="Barcelona")

        self.user = User.objects.create_user(
            email="user@upc.edu",
            full_name="Test User",
            password="secure123",
            role="student"
        )
        self.admin = User.objects.create_superuser(
            email="admin@upc.edu",
            full_name="Admin",
            password="adminpass"
        )

    # ─────────────────────────────────────────────
    # 📁 Model
    # ─────────────────────────────────────────────
    def test_profile_str(self):
        profile = Profile.objects.get(user=self.user)
        self.assertIn("Test User", str(profile))

    # ─────────────────────────────────────────────
    # 📁 Signals
    # ─────────────────────────────────────────────
    def test_profile_created_on_user_creation(self):
        new_user = User.objects.create_user(
            email="new@upc.edu",
            full_name="New User",
            password="pass123"
        )
        self.assertTrue(Profile.objects.filter(user=new_user).exists())

    # ─────────────────────────────────────────────
    # 📁 Views: MyProfileView
    # ─────────────────────────────────────────────
    def test_get_my_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/profiles/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_update_my_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch("/profiles/me/", {
            "bio": "Updated bio",
            "institution": self.institution.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio, "Updated bio")
        self.assertEqual(self.user.profile.institution, self.institution)

    # ─────────────────────────────────────────────
    # 📁 Views: Admin ViewSet
    # ─────────────────────────────────────────────
    def test_admin_can_list_profiles(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_retrieve_profile(self):
        self.client.force_authenticate(self.admin)
        profile = self.user.profile
        response = self.client.get(f"/profiles/{profile.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], self.user.email)

    def test_non_admin_cannot_list_profiles(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/profiles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ─────────────────────────────────────────────
    # 📁 Serializer Logic
    # ─────────────────────────────────────────────
    def test_profile_read_serializer_representation(self):
        self.client.force_authenticate(self.user)
        response = self.client.get("/profiles/me/")
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)
