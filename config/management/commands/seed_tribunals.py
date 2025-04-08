from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from tfms.models import TFM
from slots.models import Slot
from users.models import User

class Command(BaseCommand):
    help = "Seed test tribunals"

    def handle(self, *args, **kwargs):
        Tribunal.objects.all().delete()

        tfms = TFM.objects.all()
        slots = Slot.objects.all()
        teachers = User.objects.filter(role='teacher')

        if teachers.count() < 3 or tfms.count() == 0:
            self.stdout.write(self.style.WARNING("Not enough data to seed tribunals"))
            return

        for i, tfm in enumerate(tfms[:len(slots)]):
            slot = slots[i]
            president = teachers[0]
            secretary = teachers[1]
            vocals = teachers[2:4]

            tribunal = Tribunal.objects.create(
                tfm=tfm,
                slot=slot,
                president=president,
                secretary=secretary
            )
            tribunal.vocals.set(vocals)
            tribunal.save()

            self.stdout.write(f"Created Tribunal for {tfm.title}")
