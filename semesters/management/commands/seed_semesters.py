from django.core.management.base import BaseCommand
from semesters.models import Semester
from datetime import date, time, timedelta

class Command(BaseCommand):
    help = "Seed past, current, and future semesters"

    def handle(self, *args, **kwargs):
        semesters = [
            {
                "name": "2024-2025 Fall",
                "start_date": date(2024, 9, 16),
                "end_date": date(2025, 1, 31),
                "int_presentation_date": date(2025, 1, 20),
                "last_presentation_date": date(2025, 1, 22),
            },
            {
                "name": "2024-2025 Spring",
                "start_date": date(2025, 2, 10),
                "end_date": date(2025, 7, 11),
                "int_presentation_date": date(2025, 7, 7),
                "last_presentation_date": date(2025, 7, 9),
            },
            {
                "name": "2025-2026 Fall",
                "start_date": date(2025, 9, 15),
                "end_date": date(2026, 1, 30),
                "int_presentation_date": date(2026, 1, 18),
                "last_presentation_date": date(2026, 1, 20),
            },
        ]

        semesters_to_create = [
            Semester(
                name=data["name"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                int_presentation_date=data["int_presentation_date"],
                last_presentation_date=data["last_presentation_date"],
                daily_start_time=time(9, 0),
                daily_end_time=time(18, 0),
                pre_duration=timedelta(minutes=45),
                min_committees=3,
                max_committees=5
            )
            for data in semesters
            if not Semester.objects.filter(name=data["name"]).exists()
        ]

        if semesters_to_create:
            Semester.objects.bulk_create(semesters_to_create)
            self.stdout.write(self.style.SUCCESS(f"Created {len(semesters_to_create)} semesters"))
        else:
            self.stdout.write("⚠️ All semesters already exist")
