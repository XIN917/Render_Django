from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Semester
from django.core.exceptions import ValidationError
from datetime import date, time, timedelta
from .serializers import SemesterSerializer
from rest_framework import serializers

User = get_user_model()

class SemesterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.semester = Semester.objects.create(
            name="Spring 2025",
            start_date=date(2025, 1, 10),
            end_date=date(2025, 5, 10),
            int_presentation_date=date(2025, 5, 19),
            last_presentation_date=date(2025, 5, 23),
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

    # ─────────────────────────────────────────
    # 📁 Semester Model Validations
    # ─────────────────────────────────────────
    def test_invalid_presentation_date_range(self):
        self.semester.int_presentation_date = date(2025, 5, 25)
        self.semester.last_presentation_date = date(2025, 5, 23)
        with self.assertRaises(ValidationError):
            self.semester.clean()

    def test_invalid_semester_date_range(self):
        self.semester.start_date = date(2025, 5, 15)
        self.semester.end_date = date(2025, 5, 10)
        with self.assertRaises(ValidationError):
            self.semester.clean()

    def test_presentation_dates_on_weekend(self):
        self.semester.int_presentation_date = date(2025, 5, 17)  # Saturday
        with self.assertRaises(ValidationError):
            self.semester.clean()

        self.semester.int_presentation_date = date(2025, 5, 19)  # Reset to valid
        self.semester.last_presentation_date = date(2025, 5, 18)  # Sunday
        with self.assertRaises(ValidationError):
            self.semester.clean()

    def test_semester_dates_on_weekend(self):
        self.semester.start_date = date(2025, 1, 11)  # Saturday
        with self.assertRaises(ValidationError):
            self.semester.clean()

        self.semester.start_date = date(2025, 1, 10)  # Reset
        self.semester.end_date = date(2025, 1, 12)    # Sunday
        with self.assertRaises(ValidationError):
            self.semester.clean()

    # ─────────────────────────────────────────
    # 📁 Semester Serializer Validations
    # ─────────────────────────────────────────
    def test_serializer_semester_dates_invalid_range(self):
        data = {
            "name": "Test Semester",
            "start_date": "2025-06-01",
            "end_date": "2025-05-01",  # End before start
            "int_presentation_date": "2025-05-19",
            "last_presentation_date": "2025-05-23",
            "min_committees": 3,
            "max_committees": 5
        }
        serializer = SemesterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("start_date", serializer.errors)

    def test_serializer_semester_dates_on_weekend(self):
        data = {
            "name": "Weekend Start",
            "start_date": "2025-01-11",  # Saturday
            "end_date": "2025-05-10",
            "int_presentation_date": "2025-05-19",
            "last_presentation_date": "2025-05-23",
            "min_committees": 3,
            "max_committees": 5
        }
        serializer = SemesterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("start_date", serializer.errors)

    def test_serializer_presentation_dates_invalid_range(self):
        data = {
            "name": "Bad Presentation Dates",
            "start_date": "2025-01-10",  # Friday
            "end_date": "2025-05-09",    # Friday — not a weekend
            "int_presentation_date": "2025-05-25",  # Sunday
            "last_presentation_date": "2025-05-23",
            "min_committees": 3,
            "max_committees": 5
        }
        serializer = SemesterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("int_presentation_date", serializer.errors)

    def test_serializer_presentation_dates_on_weekend(self):
        base_data = {
            "name": "Weekend Presentations",
            "start_date": "2025-01-10",  # Friday
            "end_date": "2025-05-09",    # Friday
            "min_committees": 3,
            "max_committees": 5
        }

        # Weekend initial presentation date (Saturday)
        data = {**base_data, "int_presentation_date": "2025-05-17", "last_presentation_date": "2025-05-23"}
        serializer = SemesterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("int_presentation_date", serializer.errors)

        # Weekend last presentation date (Saturday), with valid initial date
        data = {**base_data, "int_presentation_date": "2025-05-19", "last_presentation_date": "2025-05-24"}
        serializer = SemesterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("last_presentation_date", serializer.errors)

    def test_serializer_blocks_update_if_slots_outside_new_presentation_window(self):
        # Create a slot on a date before the current int_presentation_date
        from slots.models import Slot
        track = self.semester.track_set.create(title="Track 1")
        slot = Slot.objects.create(
            date=date(2025, 5, 15),  # Before int_presentation_date
            start_time=time(10, 0),
            end_time=time(11, 0),
            max_tfms=2,
            room="A101",
            track=track
        )
        serializer = SemesterSerializer(instance=self.semester, data={
            "name": self.semester.name,
            "start_date": self.semester.start_date,
            "end_date": date(2025, 5, 9),  # Friday, not a weekend
            "int_presentation_date": date(2025, 5, 19),  # Monday, not a weekend, after slot
            "last_presentation_date": self.semester.last_presentation_date,
            "min_committees": self.semester.min_committees,
            "max_committees": self.semester.max_committees
        }, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("int_presentation_date", serializer.errors)
        self.assertIn("2025-05-15", str(serializer.errors["int_presentation_date"]))

    def test_serializer_blocks_delete_if_tracks_exist(self):
        track = self.semester.track_set.create(title="Track 1")
        serializer = SemesterSerializer()
        with self.assertRaises(serializers.ValidationError) as ctx:
            serializer.validate_delete(self.semester)
        self.assertIn("Track 1", str(ctx.exception))

    def test_serializer_allows_delete_if_no_tracks(self):
        serializer = SemesterSerializer()
        # Should not raise
        result = serializer.validate_delete(self.semester)
        self.assertEqual(result, self.semester)

    def test_delete_semester_blocked_by_track(self):
        """
        Deleting a semester referenced by a Track should return 400 with a user-friendly error message.
        """
        from tracks.models import Track
        self.client.force_authenticate(self.admin)
        # Create a track referencing self.semester
        Track.objects.create(title="Track 1", semester=self.semester)
        response = self.client.delete(f"/semesters/{self.semester.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot delete semester", response.data.get("detail", ""))
        # The semester should still exist
        self.assertTrue(Semester.objects.filter(id=self.semester.id).exists())

    def test_delete_semester_not_referenced_by_track(self):
        """
        Deleting a semester not referenced by any Track should succeed and remove the semester.
        """
        self.client.force_authenticate(self.admin)
        # Create a new semester not referenced by any track
        semester2 = Semester.objects.create(
            name="Fall 2025",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 12, 10),
            int_presentation_date=date(2025, 12, 19),
            last_presentation_date=date(2025, 12, 23),
            min_committees=3,
            max_committees=5
        )
        response = self.client.delete(f"/semesters/{semester2.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Semester.objects.filter(id=semester2.id).exists())

