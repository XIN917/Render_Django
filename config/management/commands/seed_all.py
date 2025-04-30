from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from tfms.models import TFM
from tribunals.models import Tribunal
from judges.models import Judge
from slots.models import Slot
from tracks.models import Track
from config.models import PresentationDay
import random
from datetime import datetime, date, time, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = "Seed full database with users, TFMs, slots, tracks, tribunals."

    def handle(self, *args, **kwargs):
        self.seed_users()
        self.seed_slots_and_tracks()
        self.seed_tfms()
        self.seed_tribunals()

    def seed_users(self):
        users_data = []
        
        # Admin
        users_data.append({
            "email": "admin@email.com",
            "password": "admin1234",
            "full_name": "Admin User",
            "role": "teacher",
            "is_staff": True,
            "is_superuser": True
        })

        # Teachers
        for i in range(1, 11):
            users_data.append({
                "email": f"teacher{i}@example.com",
                "password": "password123",
                "full_name": f"Dr. Teacher {i}",
                "role": "teacher"
            })

        # Students
        for i in range(1, 16):
            users_data.append({
                "email": f"student{i}@example.com",
                "password": "password123",
                "full_name": f"Student {i}",
                "role": "student"
            })

        for data in users_data:
            if not User.objects.filter(email=data["email"]).exists():
                user = User.objects.create_user(
                    email=data["email"],
                    password=data["password"],
                    full_name=data["full_name"],
                    role=data["role"]
                )
                user.is_staff = data.get("is_staff", False)
                user.is_superuser = data.get("is_superuser", False)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created: {user.email}"))
            else:
                self.stdout.write(f"⚠️  User already exists: {data['email']}")

    def seed_slots_and_tracks(self):
        presentation_day = PresentationDay.get_or_create_singleton(date(2025, 6, 15))
        self.stdout.write(self.style.SUCCESS(f"Using Presentation Day: {presentation_day.date}"))

        durations = [timedelta(minutes=45), timedelta(minutes=60)]
        times = [(8, 0), (9, 30), (11, 0), (13, 0), (14, 30)]

        room_prefixes = ['A', 'B']
        room_numbers = [101, 102, 103, 104, 105]
        rooms = [f"{prefix}{number}" for prefix in room_prefixes for number in room_numbers]

        slots = []
        for i, (h, m) in enumerate(times):
            start = time(hour=h, minute=m)
            end = (datetime.combine(date.today(), start) + durations[i % 2]).time()
            room = rooms[i % len(rooms)]

            slot, created = Slot.objects.get_or_create(
                presentation_day=presentation_day,
                start_time=start,
                end_time=end,
                room=room,
                defaults={
                    "tfm_duration": durations[i % 2],
                    "max_tfms": 2
                }
            )
            slots.append(slot)
            if created:
                self.stdout.write(f"✅ Created Slot: {slot}")
            else:
                self.stdout.write(f"⚠️  Slot already exists: {slot}")

        # Tracks
        track_titles = [
            "Technology Innovations",
            "Healthcare Advances",
            "Sustainable Development",
            "Data Science Applications",
            "Cybersecurity Solutions"
        ]

        chunk_size = max(1, len(slots) // len(track_titles))

        for i, title in enumerate(track_titles):
            track, created = Track.objects.get_or_create(title=title)
            assigned_slots = slots[i*chunk_size:(i+1)*chunk_size]
            track.slots.set(assigned_slots)
            track.save()
            self.stdout.write(self.style.SUCCESS(f"✅ {'Created' if created else 'Updated'} Track: {title}"))

        self.stdout.write(self.style.SUCCESS("✅ Tracks ensured"))

    def seed_tfms(self):
        MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 100 700 Td (Hello, PDF!) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000074 00000 n \n0000000178 00000 n \n0000000295 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n400\n%%EOF"

        students = list(User.objects.filter(role="student"))
        teachers = list(User.objects.filter(role="teacher", is_superuser=False))

        for i in range(10):
            title = f"TFM Project {i+1}"
            if TFM.objects.filter(title=title).exists():
                self.stdout.write(f"⚠️  TFM already exists: {title}")
                continue

            student = students[i % len(students)]
            directors = random.sample(teachers, k=random.randint(1,2))
            tfm = TFM.objects.create(
                title=title,
                description="Example description for project.",
                file=ContentFile(MINIMAL_PDF, name=f"tfm_{i+1}.pdf"),
                student=student
            )
            tfm.directors.set(directors)
            tfm.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created TFM: {tfm.title}"))

    def seed_tribunals(self):
        tfms = list(TFM.objects.all())
        slots = list(Slot.objects.all())
        professors = list(User.objects.filter(role="teacher", is_superuser=False))

        for i, tfm in enumerate(tfms[:len(slots)]):
            if Tribunal.objects.filter(tfm=tfm).exists():
                self.stdout.write(f"⚠️  Tribunal already exists for: {tfm.title}")
                continue

            slot = slots[i]
            tribunal = Tribunal.objects.create(tfm=tfm, slot=slot)

            roles = ['president', 'secretary', 'vocal', 'vocal']
            selected_professors = random.sample(professors, 4)

            for idx, role in enumerate(roles):
                Judge.objects.get_or_create(tribunal=tribunal, user=selected_professors[idx], role=role)

            self.stdout.write(self.style.SUCCESS(f"✅ Created Tribunal for TFM: {tfm.title}"))
