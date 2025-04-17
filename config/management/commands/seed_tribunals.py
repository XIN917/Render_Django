from django.core.management.base import BaseCommand
from tribunals.models import Tribunal, TribunalMember
from tfms.models import TFM
from slots.models import Slot
from users.models import User


class Command(BaseCommand):
    help = "Seed test tribunals"

    def handle(self, *args, **kwargs):
        Tribunal.objects.all().delete()
        TribunalMember.objects.all().delete()

        tfms = TFM.objects.all()
        slots = Slot.objects.all()
        teachers = User.objects.filter(role='teacher', is_superuser=False)

        if teachers.count() < 4 or tfms.count() == 0:
            self.stdout.write(self.style.WARNING("Not enough data to seed tribunals"))
            return

        for i, tfm in enumerate(tfms[:len(slots)]):
            slot = slots[i]
            tribunal = Tribunal.objects.create(tfm=tfm, slot=slot)

            TribunalMember.objects.create(tribunal=tribunal, user=teachers[0], role='president')
            TribunalMember.objects.create(tribunal=tribunal, user=teachers[1], role='secretary')
            TribunalMember.objects.create(tribunal=tribunal, user=teachers[2], role='vocal')
            TribunalMember.objects.create(tribunal=tribunal, user=teachers[3], role='vocal')

            self.stdout.write(self.style.SUCCESS(f"✅ Created Tribunal for TFM: {tfm.title}"))
