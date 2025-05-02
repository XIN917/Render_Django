from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from judges.models import Judge
from tfms.models import TFM
from slots.models import Slot
from users.models import User

class Command(BaseCommand):
    help = "Seed tribunals for all TFMs using available slots"

    def handle(self, *args, **kwargs):
        teachers = list(User.objects.filter(role='teacher', is_superuser=False))
        if len(teachers) < 4:
            self.stdout.write(self.style.ERROR("❌ Not enough teachers to create tribunals"))
            return

        tfms = list(TFM.objects.all())
        slots = list(Slot.objects.all())

        for i, tfm in enumerate(tfms):
            slot = slots[i % len(slots)]
            if Tribunal.objects.filter(tfm=tfm).exists():
                continue

            tribunal = Tribunal.objects.create(tfm=tfm, slot=slot)
            roles = ['president', 'secretary', 'vocal', 'vocal']
            assigned = teachers[i % len(teachers):] + teachers[:i % len(teachers)]

            for j, role in enumerate(roles):
                Judge.objects.get_or_create(tribunal=tribunal, user=assigned[j % len(teachers)], role=role)

            self.stdout.write(self.style.SUCCESS(f"✅ Tribunal created for: {tfm.title}"))
