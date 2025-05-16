from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from institutions.models import Institution

User = get_user_model()

class InstitutionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_superuser(
            email='admin@upc.edu',
            password='adminpass',
            full_name='Admin User'
        )

        self.user = User.objects.create_user(
            email='user@upc.edu',
            password='userpass',
            full_name='Regular User'
        )

        self.institution = Institution.objects.create(name="UPC", city="Barcelona")

    # ─────────────────────────────────────────────
    # 📁 Model
    # ─────────────────────────────────────────────
    def test_institution_str_method(self):
        self.assertEqual(str(self.institution), "UPC")

    # ─────────────────────────────────────────────
    # 📁 View Permissions
    # ─────────────────────────────────────────────
    def test_anonymous_can_list_institutions(self):
        response = self.client.get("/institutions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_create_institution(self):
        self.client.force_authenticate(self.user)
        response = self.client.post("/institutions/", {"name": "UAB", "city": "Cerdanyola"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_institution(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post("/institutions/", {"name": "UAB", "city": "Cerdanyola"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_update_institution(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(f"/institutions/{self.institution.id}/", {"city": "Terrassa"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.institution.refresh_from_db()
        self.assertEqual(self.institution.city, "Terrassa")

    def test_non_admin_cannot_delete_institution(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(f"/institutions/{self.institution.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_institution(self):
        self.client.force_authenticate(self.admin)
        response = self.client.delete(f"/institutions/{self.institution.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
