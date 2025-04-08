from django.core.management.base import BaseCommand
from tracks.models import Track
from slots.models import Slot

class Command(BaseCommand):
    help = "Seed test tracks"

    def handle(self, *args, **kwargs):
        Track.objects.all().delete()
        slots = Slot.objects.all()

        track = Track.objects.create(title="AI & ML")
        track.slots.set(slots[:2])
        track.save()

        track = Track.objects.create(title="Web & Backend")
        track.slots.set(slots[2:])
        track.save()

        self.stdout.write("Seeded tracks with linked slots.")

