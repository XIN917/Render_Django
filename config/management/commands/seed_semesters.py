from django.core.management.base import BaseCommand
from semesters.models import Semester
from datetime import date

class Command(BaseCommand):
    help = "Seed past, current, and future semesters"

    def handle(self, *args, **kwargs):
        semesters = [
            {
                "name": "2023-2024 Fall",
                "start_date": date(2023, 9, 1),
                "end_date": date(2024, 1, 31),
                "presentation_day": date(2024, 1, 22),
            },
            {
                "name": "2024-2025 Spring",
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 6, 30),
                "presentation_day": date(2025, 6, 16),
            },
            {
                "name": "2025-2026 Fall",
                "start_date": date(2025, 9, 1),
                "end_date": date(2026, 1, 31),
                "presentation_day": date(2026, 1, 20),
            },
        ]

        semesters_to_create = [
            Semester(
                name=data["name"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                presentation_day=data["presentation_day"],
            )
            for data in semesters
            if not Semester.objects.filter(name=data["name"]).exists()
        ]

        if semesters_to_create:
            Semester.objects.bulk_create(semesters_to_create)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(semesters_to_create)} semesters"))
        else:
            self.stdout.write("⚠️ All semesters already exist")