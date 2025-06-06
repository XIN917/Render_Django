from django.core.management.base import BaseCommand
from slots.models import Slot
from tracks.models import Track
from semesters.models import Semester
from datetime import datetime, date, time, timedelta

class Command(BaseCommand):
    help = "Seed test slots for 3 semesters with multiple tracks"

    def handle(self, *args, **kwargs):
        base_times = [(10 + i, 0) for i in range(11)]  # 10:00 to 20:00
        room_prefixes = ['A', 'B', 'C', 'D', 'E']
        room_numbers = [101, 102, 103, 201, 202, 203]
        all_rooms = [f"{p}{n}" for p in room_prefixes for n in room_numbers]

        semester_names = [
            "2024-2025 Fall",
            "2024-2025 Spring",
            "2025-2026 Fall",
        ]

        for semester_name in semester_names:
            try:
                semester = Semester.objects.get(name=semester_name)
            except Semester.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Semester '{semester_name}' not found."))
                continue

            tracks = list(Track.objects.filter(semester=semester))
            if not tracks:
                self.stdout.write(self.style.WARNING(f"⚠️ No tracks found for {semester_name}"))
                continue

            # Assign rooms to tracks in a rotating way
            track_room_map = {}
            for i, track in enumerate(tracks):
                track_rooms = all_rooms[i::len(tracks)]
                track_room_map[track.id] = track_rooms

            presentation_days = (semester.last_presentation_date - semester.int_presentation_date).days + 1

            for track in tracks:
                track_rooms = track_room_map[track.id]
                slots_to_create = []

                for day_offset in range(presentation_days):
                    slot_date = semester.int_presentation_date + timedelta(days=day_offset)
                    if slot_date.weekday() >= 5:
                        continue  # Skip weekends

                    for i, (h, m) in enumerate(base_times):
                        start = time(hour=h, minute=m)
                        duration = semester.pre_duration
                        start_dt = datetime.combine(slot_date, start)
                        end_limit_dt = datetime.combine(slot_date, semester.daily_end_time)

                        calculated_max = (end_limit_dt - start_dt) // duration
                        max_tfms = min(calculated_max, 4)
                        if max_tfms <= 0:
                            continue

                        end_dt = start_dt + duration * max_tfms
                        end = end_dt.time()

                        # Room selection from assigned subset
                        room = track_rooms[i % len(track_rooms)]

                        # Check for overlapping slots
                        overlapping = Slot.objects.filter(
                            date=slot_date,
                            room=room,
                            start_time__lt=end,
                            end_time__gt=start
                        )
                        if overlapping.exists() or start >= end:
                            continue

                        slots_to_create.append(Slot(
                            track=track,
                            date=slot_date,
                            start_time=start,
                            end_time=end,
                            room=room,
                            max_tfms=max_tfms,
                        ))

                if slots_to_create:
                    Slot.objects.bulk_create(slots_to_create)
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Created {len(slots_to_create)} slots for track: {track.title}"))
                else:
                    self.stdout.write(f"⚠️ All slots for track {track.title} already exist or conflict with others.")
