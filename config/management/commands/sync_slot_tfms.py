from django.core.management.base import BaseCommand
from tribunals.models import Tribunal

class Command(BaseCommand):
    help = "Syncs TFM-Slot relationships from Tribunal definitions"

    def handle(self, *args, **kwargs):
        count = 0
        for tribunal in Tribunal.objects.all():
            if tribunal.tfm and tribunal.slot:
                tribunal.slot.tfms.add(tribunal.tfm)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"✔ Synced {count} tribunal TFMs into slot.tfms"))
