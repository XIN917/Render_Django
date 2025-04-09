from django.core.management.base import BaseCommand
from slots.models import Slot
from tfms.models import TFM
from datetime import datetime, date, time, timedelta

class Command(BaseCommand):
    help = "Seed test slots"

    def handle(self, *args, **kwargs):
        Slot.objects.all().delete()

        durations = [timedelta(minutes=45), timedelta(minutes=60)]
        times = [(8, 0), (9, 30), (11, 0), (13, 0), (14, 30)]

        # Generate a list of rooms like A101-A105, B101-B105
        room_prefixes = ['A', 'B']
        room_numbers = [101, 102, 103, 104, 105]
        rooms = [f"{prefix}{number}" for prefix in room_prefixes for number in room_numbers]

        for i, (h, m) in enumerate(times):
            start = time(hour=h, minute=m)
            end = (datetime.combine(date.today(), start) + durations[i % 2]).time()
            room = rooms[i % len(rooms)]  # Cycle through room names
            slot = Slot.objects.create(
                start_time=start,
                end_time=end,
                tfm_duration=durations[i % 2],
                room=room
            )
            self.stdout.write(f"Created Slot {slot}")
