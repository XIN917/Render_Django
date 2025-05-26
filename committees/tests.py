from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Committee
from .serializers import CommitteeSerializer, AssignCommitteeRoleSerializer
from django.contrib.auth import get_user_model
from tribunals.models import Tribunal
from slots.models import Slot
from tracks.models import Track
from semesters.models import Semester
from tfms.models import TFM
import datetime

class CommitteeViewSetTests(APITestCase):
    def setUp(self):
        # Create required related objects
        self.User = get_user_model()
        self.user = self.User.objects.create_user(email='teacher@example.com', full_name='Teacher User', password='testpass', role='teacher')
        self.student = self.User.objects.create_user(email='student@example.com', full_name='Student User', password='testpass', role='student')
        self.superuser = self.User.objects.create_superuser(email='super@example.com', full_name='Super User', password='testpass')

        self.semester = Semester.objects.create(
            name='Spring 2025',
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 6, 30),
            int_presentation_date=datetime.date(2025, 5, 1),
            last_presentation_date=datetime.date(2025, 6, 1),
            daily_start_time=datetime.time(10, 0),
            daily_end_time=datetime.time(19, 0),
            pre_duration=datetime.timedelta(minutes=45),
            min_committees=3,
            max_committees=5
        )
        self.track = Track.objects.create(title='Track 1', semester=self.semester)
        self.slot = Slot.objects.create(date=datetime.date(2025, 5, 10), start_time=datetime.time(10, 0), end_time=datetime.time(12, 0), max_tfms=2, room='A', track=self.track)
        self.tfm = TFM.objects.create(title='TFM 1', description='desc', file='tfm1.pdf', status='approved', author=self.student)
        self.tribunal = Tribunal.objects.create(tfm=self.tfm, slot=self.slot, index=1)
        self.committee = Committee.objects.create(tribunal=self.tribunal, user=self.user, role='president')
        self.list_url = reverse('committees-list')
        self.detail_url = reverse('committees-detail', args=[self.committee.pk])

    def test_list_uses_committee_serializer(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('role', response.data[0])

    def test_retrieve_uses_committee_serializer(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('role', response.data)

    def test_create_uses_assign_committee_role_serializer_and_permissions(self):
        new_teacher = self.User.objects.create_user(email='newteacher@example.com', full_name='New Teacher', password='testpass', role='teacher')
        self.client.login(email='teacher@example.com', password='testpass')
        data = {
            'tribunal': self.tribunal.pk,
            'user': new_teacher.pk,
            'role': 'secretary'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Committee.objects.filter(tribunal=self.tribunal, user=new_teacher, role='secretary').exists())

    def test_create_requires_authentication(self):
        data = {
            'tribunal': self.tribunal.pk,
            'user': self.user.pk,
            'role': 'vocal'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_permissions_allow_any_for_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permissions_allow_any_for_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
