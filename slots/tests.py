from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import time, timedelta, date
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import tempfile
import shutil
from django.core.exceptions import ValidationError

from slots.models import Slot
from slots.serializers import SlotReadSerializer
from tfms.models import TFM
from tribunals.models import Tribunal
from tracks.models import Track
from semesters.models import Semester

User = get_user_model()

class SlotTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._temp_media = tempfile.mkdtemp()
        cls._original_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = cls._temp_media

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._temp_media)
        settings.MEDIA_ROOT = cls._original_media_root
        super().tearDownClass()

    def tearDown(self):
        for tfm in TFM.objects.all():
            if tfm.file:
                tfm.file.delete(save=False)

    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", full_name="Admin", password="adminpass",
            role=User.TEACHER, is_staff=True
        )

        self.student = User.objects.create_user(
            email="student@example.com", full_name="Student", password="studentpass",
            role=User.STUDENT
        )

        self.client.login(email="admin@example.com", password="adminpass")

        self.semester = Semester.objects.create(
            name="Test Semester",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            int_presentation_date=date(2025, 6, 15),
            last_presentation_date=date(2025, 6, 20),
            daily_start_time=time(9, 0),
            daily_end_time=time(18, 0),
            pre_duration=timedelta(minutes=45),
            min_committees=3,
            max_committees=5,
        )

        self.track = Track.objects.create(title="Test Track", semester=self.semester)

        self.slot = Slot.objects.create(
            track=self.track,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="A1",
            date=date(2025, 6, 17),
            max_tfms=2
        )

        self.tfm = TFM.objects.create(
            title="AI Thesis",
            description="A study on AI.",
            file=SimpleUploadedFile("dummy.pdf", b"dummy"),
            author=self.student,
            status="approved"
        )

        self.tribunal = Tribunal.objects.create(slot=self.slot, tfm=self.tfm)

        self.slot_url = "/slots/"

    # ──────── API Tests ────────

    def test_invalid_slot_outside_working_hours(self):
        data = {
            "track": self.track.id,
            "start_time": "07:30",
            "end_time": "08:30",
            "room": "Room 2",
            "date": "2025-06-16"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_slot_overlap_same_room(self):
        Slot.objects.create(
            track=self.track,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="Room 3",
            date="2025-06-16"
        )

        data = {
            "track": self.track.id,
            "start_time": "10:30",
            "end_time": "11:30",
            "room": "Room 3",
            "date": "2025-06-16"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_invalid_end_time_after_21(self):
        data = {
            "track": self.track.id,
            "start_time": "20:30",
            "end_time": "21:30",
            "room": "Room Y",
            "date": "2025-06-16"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.data)

    def test_end_time_before_start_time(self):
        data = {
            "track": self.track.id,
            "start_time": "11:00",
            "end_time": "10:00",
            "room": "Room Z",
            "date": "2025-06-16"
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
            "room": "Open Room",
            "date": "2025-06-16"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_serializer_used_in_post(self):
        data = {
            "track": self.track.id,
            "start_time": "13:00",
            "end_time": "14:30",
            "room": "Room A",
            "date": "2025-06-16"
        }
        response = self.client.post(self.slot_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ──────── Logic Tests ────────

    def test_slot_str_output(self):
        result = str(self.slot)
        self.assertIn("10:00", result)
        self.assertIn("A1", result)
        self.assertIn("2025-06-17", result)

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
        self.assertRegex(data["pre_duration"], r"^\d{2}:\d{2}$")

    def test_slot_date_outside_presentation_window(self):
        self.slot.date = date(2025, 6, 10)  # before int_presentation_date
        with self.assertRaises(ValidationError) as ctx:
            self.slot.clean()
        self.assertIn("Slot date must be within the allowed presentation period.", str(ctx.exception))

    def test_slot_date_on_weekend(self):
        self.slot.date = date(2025, 6, 15)  # Sunday, still weekend but inside range
        with self.assertRaises(ValidationError) as ctx:
            self.slot.clean()
        self.assertIn("Slot date cannot fall on a weekend.", str(ctx.exception))

    def test_slot_duration_too_short_for_tfms(self):
        self.slot.start_time = time(10, 0)
        self.slot.end_time = time(10, 30)  # only 30 minutes
        self.slot.max_tfms = 2  # requires 90 minutes total
        with self.assertRaises(ValidationError) as ctx:
            self.slot.clean()
        self.assertIn("Slot does not have enough time to accommodate all TFMs", str(ctx.exception))

    def test_slot_valid_clean_passes(self):
        self.slot.end_time = time(11, 30)  # extend to 90 minutes
        try:
            self.slot.clean()  # should not raise
        except ValidationError:
            self.fail("Slot.clean() raised ValidationError unexpectedly!")
