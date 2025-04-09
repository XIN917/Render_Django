from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import User
from tfms.models import TFM
from slots.models import Slot
from tribunals.models import Tribunal
from datetime import time, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

class TribunalModelTest(TestCase):
    def setUp(self):
        # Create users
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

        mock_file = SimpleUploadedFile("tfm.pdf", b"dummy content")

        self.tfm = TFM.objects.create(
            title='Test TFM',
            description='Test description',
            file=mock_file,
            status='pending',
            student=self.student,
        )
        self.tfm.directors.set([self.director])
        self.slot = Slot.objects.create(
            start_time=time(9, 0),
            end_time=time(10, 0),
            tfm_duration=timedelta(minutes=45),
            room="A101"
        )

    def test_valid_tribunal_creation(self):
        tribunal = Tribunal.objects.create(
            tfm=self.tfm,
            slot=self.slot,
            president=self.president,
            secretary=self.secretary
        )
        tribunal.vocals.set([self.vocal1, self.vocal2])
        try:
            tribunal.clean_roles()
        except ValidationError:
            self.fail("clean_roles() raised ValidationError unexpectedly!")

    def test_conflicting_roles(self):
        tribunal = Tribunal.objects.create(
            tfm=self.tfm,
            slot=self.slot,
            president=self.president,
            secretary=self.secretary
        )
        tribunal.vocals.set([self.president])  # conflict!
        with self.assertRaises(ValidationError):
            tribunal.clean_roles()

    def test_missing_vocal(self):
        tribunal = Tribunal.objects.create(
            tfm=self.tfm,
            slot=self.slot,
            president=self.president,
            secretary=self.secretary
        )
        tribunal.vocals.set([])  # no vocals
        with self.assertRaises(ValidationError):
            tribunal.clean_roles()
