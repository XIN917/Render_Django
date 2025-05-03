from django.core.management.base import BaseCommand
from slots.models import Slot
from tracks.models import Track
from semesters.models import Semester
from datetime import datetime, date, time, timedelta

class Command(BaseCommand):
    help = "Seed test slots for 3 semesters with multiple tracks"

    def handle(self, *args, **kwargs):
        durations = [timedelta(minutes=45), timedelta(minutes=60)]
        base_times = [(8 + i, 0) for i in range(8)]  # 8:00 to 15:00
        room_prefixes = ['A', 'B', 'C']
        room_numbers = [101, 102, 103]
        rooms = [f"{p}{n}" for p in room_prefixes for n in room_numbers]

        semester_names = [
            "2023-2024 Fall",
            "2024-2025 Spring",
            "2025-2026 Fall"
        ]

        for semester_name in semester_names:
            try:
                semester = Semester.objects.get(name=semester_name)
            except Semester.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Semester '{semester_name}' not found."))
                continue

            tracks = Track.objects.filter(semester=semester)
            for track in tracks:
                for i, (h, m) in enumerate(base_times):
                    start = time(hour=h, minute=m)
                    end = (datetime.combine(date.today(), start) + durations[i % 2]).time()
                    room = rooms[i % len(rooms)]

                    if not Slot.objects.filter(track=track, start_time=start, room=room).exists():
                        Slot.objects.create(
                            track=track,
                            start_time=start,
                            end_time=end,
                            tfm_duration=durations[i % 2],
                            room=room,
                            max_tfms=2
                        )
                self.stdout.write(self.style.SUCCESS(f"✅ Slots ensured for track: {track.title}"))
