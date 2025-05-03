# seed_tribunals.py

from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from tfms.models import TFM
from users.models import User
from slots.models import Slot
from judges.models import Judge
import random

class Command(BaseCommand):
    help = "Seed tribunals and assign judges"

    def handle(self, *args, **kwargs):
        tfms = list(TFM.objects.all())
        slots = list(Slot.objects.filter(tribunals__isnull=True))
        teachers = list(User.objects.filter(role="teacher", is_superuser=False))

        if not slots:
            self.stdout.write(self.style.WARNING("⚠️ No available slots for tribunal assignment"))
            return

        for i, tfm in enumerate(tfms):
            if Tribunal.objects.filter(tfm=tfm).exists():
                self.stdout.write(self.style.WARNING(f"⚠️ Tribunal already exists for TFM: {tfm.title}"))
                continue

            available_slots = [s for s in slots if not s.is_full()]
            if not available_slots:
                self.stdout.write(self.style.WARNING(f"ℹ️ No available slots to assign TFM '{tfm.title}'"))
                continue

            slot = available_slots[i % len(available_slots)]
            tribunal = Tribunal.objects.create(tfm=tfm, slot=slot)

            judges = random.sample(teachers, k=3)
            roles = ["president", "secretary", "vocal"]
            for user, role in zip(judges, roles):
                Judge.objects.create(tribunal=tribunal, user=user, role=role)

            self.stdout.write(self.style.SUCCESS(f"✅ Created tribunal for TFM: {tfm.title}"))
