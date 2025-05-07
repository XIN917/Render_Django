from django.core.management.base import BaseCommand
from slots.models import Slot
from tracks.models import Track
from semesters.models import Semester
from datetime import datetime, date, time, timedelta

class Command(BaseCommand):
    help = "Seed test slots for 3 semesters with multiple tracks"

    def handle(self, *args, **kwargs):
        durations = [timedelta(minutes=45), timedelta(minutes=60)]
        base_times = [(10 + i, 0) for i in range(11)]  # 10:00 to 20:00
        room_prefixes = ['A', 'B', 'C']
        room_numbers = [101, 102, 103]
        rooms = [f"{p}{n}" for p in room_prefixes for n in room_numbers]

        semester_names = [
            "2023-2024 Fall",
            "2024-2025 Spring",
            "2025-2026 Fall",
        ]

        for semester_name in semester_names:
            try:
                semester = Semester.objects.get(name=semester_name)
            except Semester.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Semester '{semester_name}' not found."))
                continue

            tracks = Track.objects.filter(semester=semester)
            for track in tracks:
                existing_slots = Slot.objects.filter(track=track).values_list("start_time", "room")
                existing_slots_set = set(existing_slots)

                slots_to_create = []
                for i, (h, m) in enumerate(base_times):
                    start = time(hour=h, minute=m)
                    tfm_duration = durations[i % 2]
                    max_tfms = 2  # Default value

                    # Calculate the potential end time
                    potential_end = (datetime.combine(date.today(), start) + tfm_duration * max_tfms).time()

                    # Adjust max_tfms if potential_end exceeds 21:00
                    if potential_end > time(21, 0):
                        max_tfms = (datetime.combine(date.today(), time(21, 0)) - datetime.combine(date.today(), start)) // tfm_duration
                        if max_tfms <= 0:
                            break  # Skip this slot if no valid max_tfms can be set

                    end = (datetime.combine(date.today(), start) + tfm_duration * max_tfms).time()
                    room = rooms[i % len(rooms)]

                    if (start, room) not in existing_slots_set:
                        slots_to_create.append(Slot(
                            track=track,
                            start_time=start,
                            end_time=end,
                            tfm_duration=tfm_duration,
                            room=room,
                            max_tfms=max_tfms,
                        ))

                if slots_to_create:
                    Slot.objects.bulk_create(slots_to_create)
                    self.stdout.write(self.style.SUCCESS(f"✅ Created {len(slots_to_create)} slots for track: {track.title}"))
                else:
                    self.stdout.write(f"⚠️ All slots for track {track.title} already exist")