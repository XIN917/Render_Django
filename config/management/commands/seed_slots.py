from django.core.management.base import BaseCommand
from slots.models import Slot
from config.models import PresentationDay
from datetime import datetime, date, time, timedelta


class Command(BaseCommand):
    help = "Seed test slots for the active PresentationDay"

    def handle(self, *args, **kwargs):
        Slot.objects.all().delete()

        # Get or create the singleton presentation day with fixed or custom date
        presentation_day = PresentationDay.get_or_create_singleton(date(2025, 6, 15))
        self.stdout.write(self.style.SUCCESS(f"Using Presentation Day: {presentation_day.date}"))

        durations = [timedelta(minutes=45), timedelta(minutes=60)]
        times = [(8, 0), (9, 30), (11, 0), (13, 0), (14, 30)]

        room_prefixes = ['A', 'B']
        room_numbers = [101, 102, 103, 104, 105]
        rooms = [f"{prefix}{number}" for prefix in room_prefixes for number in room_numbers]

        for i, (h, m) in enumerate(times):
            start = time(hour=h, minute=m)
            end = (datetime.combine(date.today(), start) + durations[i % 2]).time()
            room = rooms[i % len(rooms)]

            slot = Slot.objects.create(
                presentation_day=presentation_day,
                start_time=start,
                end_time=end,
                tfm_duration=durations[i % 2],
                room=room,
                max_tfms=2,
            )
            self.stdout.write(f"✅ Created Slot: {slot}")
