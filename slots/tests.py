from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from config.models import PresentationDay
from slots.models import Slot
from datetime import time

User = get_user_model()


class SlotAPITest(APITestCase):
    def setUp(self):
        # Create users
        self.admin = User.objects.create_user(
            email="admin@example.com",
            full_name="Admin",
            password="adminpass",
            role=User.TEACHER,
            is_staff=True
        )

        self.student = User.objects.create_user(
            email="student@example.com",
            full_name="Student",
            password="studentpass",
            role=User.STUDENT
        )

        # Authenticate as admin
        self.client.login(email="admin@example.com", password="adminpass")

        # Create presentation day
        self.presentation_day = PresentationDay.get_or_create_singleton()

        self.slot_url = "/slots/"  # Make sure this matches your actual router path

    def test_invalid_slot_not_on_half_hour(self):
        data = {
            "presentation_day": self.presentation_day.id,
            "start_time": "08:10",
            "end_time": "09:00",
            "room": "Room 1"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_invalid_slot_outside_working_hours(self):
        data = {
            "presentation_day": self.presentation_day.id,
            "start_time": "07:30",
            "end_time": "08:30",
            "room": "Room 2"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_slot_overlap_same_room(self):
        # Create a valid slot first
        Slot.objects.create(
            presentation_day=self.presentation_day,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="Room 3"
        )

        # Attempt overlapping slot
        data = {
            "presentation_day": self.presentation_day.id,
            "start_time": "10:30",
            "end_time": "11:30",
            "room": "Room 3"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
