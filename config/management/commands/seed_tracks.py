from django.core.management.base import BaseCommand
from tracks.models import Track
from slots.models import Slot

class Command(BaseCommand):
    help = "Seed test tracks"

    def handle(self, *args, **kwargs):
        Track.objects.all().delete()
        slots = Slot.objects.all()

        track = Track.objects.create(title="Track 1")
        track.slots.set(slots[:2])
        track.save()

        track = Track.objects.create(title="Track 2")
        track.slots.set(slots[2:])
        track.save()

        self.stdout.write("Seeded tracks with linked slots.")

