from django.core.management.base import BaseCommand
from tracks.models import Track
from slots.models import Slot
from semester.models import Semester

class Command(BaseCommand):
    help = "Seed 5 tracks per semester and assign available slots"

    def handle(self, *args, **kwargs):
        semesters = {
            "2023-2024 Fall": [
                "Data Engineering Fundamentals",
                "Mobile App Development",
                "Smart City Infrastructures",
                "Quantum Cryptography",
                "Ethics in Artificial Intelligence"
            ],
            "2024-2025 Spring": [
                "AI and Machine Learning",
                "Health Informatics",
                "Blockchain Applications",
                "Sustainable Technology",
                "Cybersecurity and Privacy"
            ],
            "2025-2026 Fall": [
                "Augmented Reality Design",
                "Human-Robot Interaction",
                "Energy-Efficient Computing",
                "Digital Transformation in Industry",
                "Autonomous Systems Engineering"
            ]
        }

        for semester_name, track_titles in semesters.items():
            try:
                semester = Semester.objects.get(name=semester_name)
            except Semester.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️ Semester not found: {semester_name}"))
                continue

            unassigned_slots = Slot.objects.filter(track__isnull=True, track__semester=semester) | Slot.objects.filter(track__semester=semester, track=None)
            slot_chunks = [list(unassigned_slots[i::len(track_titles)]) for i in range(len(track_titles))]

            for i, title in enumerate(track_titles):
                track, created = Track.objects.get_or_create(title=title, semester=semester)
                if slot_chunks[i]:
                    track.slots.set(slot_chunks[i])
                    self.stdout.write(self.style.SUCCESS(f"✅ {'Created' if created else 'Updated'} track '{title}' with {len(slot_chunks[i])} slots"))
                else:
                    self.stdout.write(f"ℹ️ No available slots to assign to '{title}'")

        self.stdout.write(self.style.SUCCESS("🎯 Finished seeding tracks for all semesters."))
