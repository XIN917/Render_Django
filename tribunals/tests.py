from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import User
from tfms.models import TFM
from slots.models import Slot
from tribunals.models import Tribunal, TribunalMember
from config.models import PresentationDay
from datetime import time, timedelta, date
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

        # Create mock file
        mock_file = SimpleUploadedFile("tfm.pdf", b"dummy content")

        # Create TFM
        self.tfm = TFM.objects.create(
            title='Test TFM',
            description='Test description',
            file=mock_file,
            status='pending',
            student=self.student,
        )
        self.tfm.directors.set([self.director])

        # Create PresentationDay (singleton)
        self.presentation_day = PresentationDay.get_or_create_singleton()
        
        # Create Slot
        self.slot = Slot.objects.create(
            presentation_day=self.presentation_day,
            start_time=time(9, 0),
            end_time=time(10, 0),
            tfm_duration=timedelta(minutes=45),
            room="A101"
        )

    def test_valid_tribunal_creation(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        TribunalMember.objects.create(tribunal=tribunal, user=self.president, role='president')
        TribunalMember.objects.create(tribunal=tribunal, user=self.secretary, role='secretary')
        TribunalMember.objects.create(tribunal=tribunal, user=self.vocal1, role='vocal')
        TribunalMember.objects.create(tribunal=tribunal, user=self.vocal2, role='vocal')

        self.assertEqual(tribunal.members.count(), 4)

    def test_conflicting_roles(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        TribunalMember.objects.create(tribunal=tribunal, user=self.president, role='president')
        with self.assertRaises(ValidationError):
            # Attempt to assign same user again to another role
            member = TribunalMember(tribunal=tribunal, user=self.president, role='vocal')
            member.full_clean()

    def test_missing_vocal(self):
        tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot)
        TribunalMember.objects.create(tribunal=tribunal, user=self.president, role='president')
        TribunalMember.objects.create(tribunal=tribunal, user=self.secretary, role='secretary')

        vocals = TribunalMember.objects.filter(tribunal=tribunal, role='vocal')
        self.assertEqual(vocals.count(), 0)
