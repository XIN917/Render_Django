from rest_framework.test import APITestCase
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import time, timedelta, date, datetime
import tempfile

from users.models import User
from tfms.models import TFM
from slots.models import Slot
from tribunals.models import Tribunal
from committees.models import Committee
from tracks.models import Track
from semesters.models import Semester
from tribunals.serializers import TribunalSerializer, TribunalReadSerializer
from tribunals.views import TribunalViewSet

class TribunalTests(APITestCase):
    
    def tearDown(self):
        for tfm in TFM.objects.all():
            if tfm.file:
                tfm.file.delete(save=False)
        
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com', full_name='Admin', password='adminpass',
            role='teacher', is_staff=True
        )
        self.student = User.objects.create_user(
            email='student@example.com', full_name='Student User', password='test', role='student'
        )
        self.director = User.objects.create_user(
            email='director@example.com', full_name='Director User', password='test', role='teacher'
        )
        self.president = User.objects.create_user(
            email='president@example.com', full_name='President User', password='test', role='teacher'
        )
        self.secretary = User.objects.create_user(
            email='secretary@example.com', full_name='Secretary User', password='test', role='teacher'
        )
        self.vocal1 = User.objects.create_user(
            email='vocal1@example.com', full_name='Vocal One', password='test', role='teacher'
        )
        self.vocal2 = User.objects.create_user(
            email='vocal2@example.com', full_name='Vocal Two', password='test', role='teacher'
        )

        self.semester = Semester.objects.create(
            name="Spring 2025", start_date=date(2025, 2, 1), end_date=date(2025, 6, 30),
            int_presentation_date=date(2025, 6, 15), last_presentation_date=date(2025, 6, 20),
            daily_start_time=time(8, 0), daily_end_time=time(18, 0),
            pre_duration=timedelta(minutes=45), min_committees=3, max_committees=5
        )

        self.track = Track.objects.create(title="Test Track", semester=self.semester)

        mock_file = SimpleUploadedFile("tfm.pdf", b"dummy content")
        self.tfm = TFM.objects.create(
            title='Test TFM', description='Test description', file=mock_file,
            status='pending', author=self.student
        )
        self.tfm.directors.set([self.director])

        self.slot = Slot.objects.create(
            track=self.track, start_time=time(9, 0), end_time=time(10, 30),
            room="A101", date=date(2025, 6, 17), max_tfms=2
        )

    # ──────── Model Tests ────────

    def test_valid_tribunal_creation(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        Committee.objects.create(tribunal=tribunal, user=self.president, role='president')
        Committee.objects.create(tribunal=tribunal, user=self.secretary, role='secretary')
        Committee.objects.create(tribunal=tribunal, user=self.vocal1, role='vocal')
        Committee.objects.create(tribunal=tribunal, user=self.vocal2, role='vocal')
        self.assertEqual(tribunal.committees.count(), 4)

    def test_add_committee_helper(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        committee = tribunal.add_committee(user=self.president, role='president')
        self.assertEqual(committee.tribunal, tribunal)

    def test_conflicting_roles(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        Committee.objects.create(tribunal=tribunal, user=self.president, role='president')
        with self.assertRaises(ValidationError):
            duplicate = Committee(tribunal=tribunal, user=self.president, role='vocal')
            duplicate.full_clean()

    def test_missing_vocal(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        Committee.objects.create(tribunal=tribunal, user=self.president, role='president')
        Committee.objects.create(tribunal=tribunal, user=self.secretary, role='secretary')
        vocals = Committee.objects.filter(tribunal=tribunal, role='vocal')
        self.assertEqual(vocals.count(), 0)

    def test_is_ready_and_full(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        for i, user in enumerate([self.president, self.secretary, self.vocal1, self.vocal2]):
            Committee.objects.create(
                tribunal=tribunal,
                user=user,
                role='vocal' if i >= 2 else ['president', 'secretary'][i]
            )
        self.assertFalse(tribunal.is_full())
        Committee.objects.create(
            tribunal=tribunal,
            user=User.objects.create_user(full_name='Fifth User', email='fifth@test.com', role='teacher'),
            role='vocal'
        )
        self.assertTrue(tribunal.is_full())
        self.assertTrue(tribunal.is_ready())

    def test_tribunal_str_output(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        self.assertEqual(str(tribunal), f"Tribunal for {self.tfm.title}")

    def test_manual_index_one_when_available(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot, index=1)
        self.assertEqual(tribunal.index, 1)

    def test_auto_index_assignment_when_slot_fills(self):
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        tfm2 = TFM.objects.create(title='Another TFM', file=SimpleUploadedFile("tfm2.pdf", b"data"),
                                  author=self.student, status='pending')
        tfm2.directors.set([self.director])
        second = Tribunal.objects.create(tfm=tfm2, slot=self.slot)
        self.assertEqual(second.index, 2)

    def test_tribunal_auto_index_skips_used(self):
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot, index=1)
        tfm2 = TFM.objects.create(title="Second", file=SimpleUploadedFile("s.pdf", b"x"), author=self.student)
        tfm2.directors.set([self.director])
        tribunal2 = Tribunal.objects.create(tfm=tfm2, slot=self.slot)
        self.assertEqual(tribunal2.index, 2)

    # ──────── Serializer Tests ────────

    def test_tribunal_serializer_validates_index_conflict(self):
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot, index=1)
        tfm2 = TFM.objects.create(title="New", file=SimpleUploadedFile("a.pdf", b"data"),
                                  author=self.student, status="pending")
        serializer = TribunalSerializer(data={"tfm": tfm2.id, "slot": self.slot.id, "index": 1})
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertIn("must make a unique set", str(serializer.errors["non_field_errors"]))

    def test_serializer_requires_slot(self):
        serializer = TribunalSerializer(data={"tfm": self.tfm.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn("slot", serializer.errors)
        self.assertIn("This field is required.", str(serializer.errors["slot"]))

    def test_validate_slot_when_instance_slot_is_same(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        serializer = TribunalSerializer(instance=tribunal)
        validated_slot = serializer.validate_slot(self.slot)
        self.assertEqual(validated_slot, self.slot)

    def test_validate_slot_rejects_when_full(self):
        self.slot.max_tfms = 0
        self.slot.save()
        serializer = TribunalSerializer()
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_slot(self.slot)

    def test_serializer_update_recalculates_old_and_new_slots(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        new_slot = Slot.objects.create(track=self.track, start_time=time(11, 0), end_time=time(11, 0),
                                       date=date(2025, 6, 18), room="Room B", max_tfms=2)
        serializer = TribunalSerializer(instance=tribunal, data={"slot": new_slot.id}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.slot.id, new_slot.id)

    def test_recalculate_slot_end_time_manual(self):
        serializer = TribunalSerializer()
        self.slot.end_time = time(10, 0)
        self.slot.save()
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        serializer._recalculate_slot_end_time(self.slot)
        self.slot.refresh_from_db()
        expected = (datetime.combine(date.today(), self.slot.start_time) + self.slot.track.semester.pre_duration).time()
        self.assertEqual(self.slot.end_time, expected)

    def test_read_serializer_times(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot, index=1)
        serializer = TribunalReadSerializer(instance=tribunal)
        self.assertIn("start_time", serializer.data)
        self.assertIn("end_time", serializer.data)

    # ──────── Signal Tests ────────

    def test_slot_end_time_updated_on_tribunal_save(self):
        self.slot.end_time = self.slot.start_time
        self.slot.save()
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        self.slot.refresh_from_db()
        expected_end = (datetime.combine(date.today(), self.slot.start_time) + self.semester.pre_duration).time()
        self.assertEqual(self.slot.end_time, expected_end)

    def test_tribunal_delete_updates_slot_end_time(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        self.slot.refresh_from_db()
        self.assertNotEqual(self.slot.end_time, self.slot.start_time)
        tribunal.delete()
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.end_time, self.slot.start_time)

    # ──────── View/API Tests ────────

    def test_get_serializer_class_default(self):
        view = TribunalViewSet()
        view.action = "create"
        serializer_class = view.get_serializer_class()
        self.assertEqual(serializer_class, TribunalSerializer)

    def test_auto_assign_valid_role(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        self.client.force_authenticate(user=self.president)
        response = self.client.post(f"/tribunals/{tribunal.id}/auto_assign/", {"role": "president"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("assigned as president", response.data["detail"].lower())

    def test_auto_assign_invalid_role(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        self.client.force_authenticate(user=self.student)
        response = self.client.post(f"/tribunals/{tribunal.id}/auto_assign/", {"role": "invalid"})
        self.assertEqual(response.status_code, 400)

    def test_available_and_ready_tribunals(self):
        self.client.force_authenticate(user=self.admin)
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        response = self.client.get("/tribunals/available/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/tribunals/ready/")
        self.assertEqual(response.status_code, 200)

    def test_available_and_ready_tribunals_empty(self):
        Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        self.client.force_authenticate(user=self.admin)
        resp1 = self.client.get("/tribunals/available/")
        resp2 = self.client.get("/tribunals/ready/")
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp1.data), 1)
        self.assertEqual(len(resp2.data), 0)
