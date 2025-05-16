from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import time, timedelta
from slots.models import Slot
from slots.serializers import SlotReadSerializer
from tfms.models import TFM
from profiles.models import Profile
from tribunals.models import Tribunal
from tracks.models import Track
from semesters.models import Semester

User = get_user_model()


class SlotAPITest(APITestCase):
    def setUp(self):
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

        self.client.login(email="admin@example.com", password="adminpass")

        self.semester = Semester.objects.create(
            name="Test Semester",
            start_date="2025-01-01",
            end_date="2025-06-30",
            presentation_day="2025-06-15"
        )

        self.track = Track.objects.create(title="Test Track", semester=self.semester)
        self.slot_url = "/slots/"

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
        Slot.objects.create(
            track=self.track,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="Room 3"
        )

        data = {
            "track": self.track.id,
            "start_time": "10:30",
            "end_time": "11:30",
            "room": "Room 3"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
    
    def test_invalid_end_time_not_on_quarter_hour(self):
        data = {
            "track": self.track.id,
            "start_time": "10:00",
            "end_time": "10:17",
            "room": "Room X"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.data)

    def test_invalid_end_time_after_21(self):
        data = {
            "track": self.track.id,
            "start_time": "20:30",
            "end_time": "21:30",
            "room": "Room Y"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.data)

    def test_end_time_before_start_time(self):
        data = {
            "track": self.track.id,
            "start_time": "11:00",
            "end_time": "10:00",
            "room": "Room Z"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.data)

    def test_create_slot_requires_authentication(self):
        self.client.logout()
        data = {
            "track": self.track.id,
            "start_time": "10:00",
            "end_time": "11:00",
            "room": "Open Room"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serializer_used_in_post(self):
        data = {
            "track": self.track.id,
            "start_time": "13:00",
            "end_time": "14:00",
            "room": "Room A"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



class SlotLogicTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.semester = Semester.objects.create(
            name="Spring",
            start_date="2025-01-01",
            end_date="2025-06-30",
            presentation_day="2025-06-20",
            min_judges=2,
            max_judges=4
        )
        self.track = Track.objects.create(title="AI", semester=self.semester)
        self.slot = Slot.objects.create(
            track=self.track,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="A1"
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            full_name="Student",
            password="testpass",
            role="student"
        )
        self.tfm = TFM.objects.create(
            title="AI Thesis",
            description="A study on AI.",
            file="dummy.pdf",
            author=self.student,
            status="approved"
        )
        self.tribunal = Tribunal.objects.create(slot=self.slot, tfm=self.tfm)

    def test_slot_str_output(self):
        result = str(self.slot)
        self.assertIn("10:00", result)
        self.assertIn("A1", result)
        self.assertIn("2025-06-20", result)

    def test_slot_is_full_logic(self):
        self.slot.max_tfms = 1
        self.slot.save()
        self.assertTrue(self.slot.is_full())

    def test_get_tfms_returns_tfm(self):
        tfms = self.slot.get_tfms()
        self.assertIn(self.tfm, tfms)

    def test_slot_read_serializer_fields(self):
        serializer = SlotReadSerializer(instance=self.slot)
        data = serializer.data
        self.assertIn("tfms", data)
        self.assertIn("is_full", data)
        self.assertEqual(data["is_full"], False)
        self.assertRegex(data["tfm_duration"], r"^\d{2}:\d{2}$") 
