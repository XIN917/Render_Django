from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import time, timedelta, date

from users.models import User
from tfms.models import TFM
from slots.models import Slot
from tribunals.models import Tribunal
from judges.models import Judge
from tracks.models import Track
from semester.models import Semester

class TribunalModelTest(TestCase):
    def setUp(self):
        # Users
        self.student = User.objects.create_user(
            email='student@example.com',
            full_name='Student User',
            password='test',
            role='student'
        )
        self.director = User.objects.create_user(
            email='director@example.com',
            full_name='Director User',
            password='test',
            role='teacher'
        )
        self.president = User.objects.create_user(
            email='president@example.com',
            full_name='President User',
            password='test',
            role='teacher'
        )
        self.secretary = User.objects.create_user(
            email='secretary@example.com',
            full_name='Secretary User',
            password='test',
            role='teacher'
        )
        self.vocal1 = User.objects.create_user(
            email='vocal1@example.com',
            full_name='Vocal One',
            password='test',
            role='teacher'
        )
        self.vocal2 = User.objects.create_user(
            email='vocal2@example.com',
            full_name='Vocal Two',
            password='test',
            role='teacher'
        )

        # Semester and Track (required by Slot)
        self.semester = Semester.objects.create(
            name="Spring 2025",
            start_date=date(2025, 2, 1),
            end_date=date(2025, 6, 30),
            presentation_day=date(2025, 6, 15)
        )

        self.track = Track.objects.create(
            title="Test Track",
            semester=self.semester
        )

        # TFM
        mock_file = SimpleUploadedFile("tfm.pdf", b"dummy content")
        self.tfm = TFM.objects.create(
            title='Test TFM',
            description='Test description',
            file=mock_file,
            status='pending',
            student=self.student,
        )
        self.tfm.directors.set([self.director])

        # Slot (now linked to a track)
        self.slot = Slot.objects.create(
            track=self.track,
            start_time=time(9, 0),
            end_time=time(10, 0),
            tfm_duration=timedelta(minutes=45),
            room="A101"
        )

    def test_valid_tribunal_creation(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        Judge.objects.create(tribunal=tribunal, user=self.president, role='president')
        Judge.objects.create(tribunal=tribunal, user=self.secretary, role='secretary')
        Judge.objects.create(tribunal=tribunal, user=self.vocal1, role='vocal')
        Judge.objects.create(tribunal=tribunal, user=self.vocal2, role='vocal')

        self.assertEqual(tribunal.judge_entries.count(), 4)

    def test_conflicting_roles(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        Judge.objects.create(tribunal=tribunal, user=self.president, role='president')
        with self.assertRaises(ValidationError):
            duplicate = Judge(tribunal=tribunal, user=self.president, role='vocal')
            duplicate.full_clean()

    def test_missing_vocal(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        Judge.objects.create(tribunal=tribunal, user=self.president, role='president')
        Judge.objects.create(tribunal=tribunal, user=self.secretary, role='secretary')

        vocals = Judge.objects.filter(tribunal=tribunal, role='vocal')
        self.assertEqual(vocals.count(), 0)
