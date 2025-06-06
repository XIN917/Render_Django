from django.core.management.base import BaseCommand
from tracks.models import Track
from semesters.models import Semester

class Command(BaseCommand):
    help = "Seed 5 tracks per semester (without assigning slots)"

    def handle(self, *args, **kwargs):
        semesters = {
            "2024-2025 Fall": [
                "T1: Data Engineering Fundamentals",
                "T2: Mobile App Development",
                "T3: Smart City Infrastructures",
                "T4: Quantum Cryptography",
                "T5: Ethics in Artificial Intelligence",
            ],
            "2024-2025 Spring": [
                "T1: AI and Machine Learning",
                "T2: Health Informatics",
                "T3: Blockchain Applications",
                "T4: Sustainable Technology",
                "T5: Cybersecurity and Privacy",
            ],
            "2025-2026 Fall": [
                "T1: Augmented Reality Design",
                "T2: Human-Robot Interaction",
                "T3: Energy-Efficient Computing",
                "T4: Digital Transformation in Industry",
                "T5: Autonomous Systems Engineering",
            ],
        }

        for semester_name, track_titles in semesters.items():
            try:
                semester = Semester.objects.get(name=semester_name)
            except Semester.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️ Semester not found: {semester_name}"))
                continue

            tracks_to_create = [
                Track(title=title, semester=semester)
                for title in track_titles
                if not Track.objects.filter(title=title, semester=semester).exists()
            ]

            if tracks_to_create:
                Track.objects.bulk_create(tracks_to_create)
                self.stdout.write(self.style.SUCCESS(f"Created {len(tracks_to_create)} tracks for {semester_name}"))
            else:
                self.stdout.write(f"⚠️ All tracks for {semester_name} already exist")