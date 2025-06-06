from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from semesters.models import Semester
from tracks.models import Track

User = get_user_model()

class TrackAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a Semester instance
        self.semester = Semester.objects.create(
            name="2024-2025 Spring",
            start_date=date(2025, 2, 10),
            end_date=date(2025, 7, 10),
            int_presentation_date=date(2025, 6, 25),
            last_presentation_date=date(2025, 6, 28),
            daily_start_time=time(9, 0),
            daily_end_time=time(17, 0),
            pre_duration=timedelta(minutes=45),
            min_committees=3,
            max_committees=5
        )

        # Users
        self.admin = User.objects.create_user(
            full_name="Admin", email="admin@test.com", password="adminpass",
            role=User.TEACHER, is_staff=True, is_superuser=True
        )
        self.student = User.objects.create_user(
            full_name="Student", email="student@test.com", password="studentpass",
            role=User.STUDENT
        )

        # One track
        self.track = Track.objects.create(title="AI Track", semester=self.semester)

    def test_semester_str(self):
        self.assertEqual(str(self.semester), "2024-2025 Spring")

    def test_track_str(self):
        self.assertEqual(str(self.track), "AI Track")

    def test_list_tracks_public(self):
        response = self.client.get("/tracks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "AI Track")

    def test_retrieve_track_public(self):
        response = self.client.get(f"/tracks/{self.track.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "AI Track")

    def test_create_track_requires_auth(self):
        response = self.client.post("/tracks/", {
            "title": "New Track", "semester": self.semester.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_track_authenticated(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/tracks/", {
            "title": "New Track", "semester": self.semester.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Track")

    def test_update_track(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f"/tracks/{self.track.id}/", {
            "title": "Updated Track"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.track.refresh_from_db()
        self.assertEqual(self.track.title, "Updated Track")

    def test_delete_track(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"/tracks/{self.track.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Track.objects.filter(id=self.track.id).exists())

    def test_delete_track_blocked_by_slot(self):
        """
        Deleting a track referenced by a Slot should return 400 with a user-friendly error message.
        """
        from slots.models import Slot
        self.client.force_authenticate(user=self.admin)
        # Create a slot referencing self.track
        Slot.objects.create(
            track=self.track,
            start_time=time(10, 0),
            end_time=time(11, 0),
            room="A1",
            date=date(2025, 6, 20),
            max_tfms=2
        )
        response = self.client.delete(f"/tracks/{self.track.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot delete track", response.data.get("detail", ""))
        # The track should still exist
        self.assertTrue(Track.objects.filter(id=self.track.id).exists())

    def test_delete_track_not_referenced_by_slot(self):
        """
        Deleting a track not referenced by any Slot should succeed and remove the track.
        """
        self.client.force_authenticate(user=self.admin)
        # Create a new track not referenced by any slot
        track2 = Track.objects.create(title="Unreferenced Track", semester=self.semester)
        response = self.client.delete(f"/tracks/{track2.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Track.objects.filter(id=track2.id).exists())
