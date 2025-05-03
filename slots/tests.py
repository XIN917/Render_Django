from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from slots.models import Slot
from tracks.models import Track
from semesters.models import Semester
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

        # Create a semester and a track
        self.semester = Semester.objects.create(
            name="Test Semester",
            start_date="2025-01-01",
            end_date="2025-06-30",
            presentation_day="2025-06-15"
        )

        self.track = Track.objects.create(title="Test Track", semester=self.semester)

        self.slot_url = "/slots/"  # Ensure this matches your router path

    def test_invalid_slot_not_on_half_hour(self):
        data = {
            "track": self.track.id,
            "start_time": "08:10",
            "end_time": "09:00",
            "room": "Room 1"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_invalid_slot_outside_working_hours(self):
        data = {
            "track": self.track.id,
            "start_time": "07:30",
            "end_time": "08:30",
            "room": "Room 2"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_slot_overlap_same_room(self):
        # Create a valid existing slot
        Slot.objects.create(
            track=self.track,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="Room 3"
        )

        # Attempt to create an overlapping slot in same room and track
        data = {
            "track": self.track.id,
            "start_time": "10:30",
            "end_time": "11:30",
            "room": "Room 3"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
