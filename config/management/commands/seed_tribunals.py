from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from judges.models import Judge
from tfms.models import TFM
from slots.models import Slot
from users.models import User

class Command(BaseCommand):
    help = "Seed test tribunals and auto-assign teachers as judges"

    def handle(self, *args, **kwargs):
        # Clear existing tribunals and judges if you want to reset
        Tribunal.objects.all().delete()
        Judge.objects.all().delete()

        tfms = TFM.objects.all()
        slots = Slot.objects.all()
        teachers = User.objects.filter(role='teacher', is_superuser=False)

        if teachers.count() < 4 or tfms.count() == 0:
            self.stdout.write(self.style.WARNING("Not enough data to seed tribunals"))
            return

        for i, tfm in enumerate(tfms[:len(slots)]):
            slot = slots[i]
            # Create a tribunal with TFM and Slot
            tribunal = Tribunal.objects.create(tfm=tfm, slot=slot)

            # Auto-assign teachers to tribunal
            roles = ['president', 'secretary', 'vocal', 'vocal']
            for idx, role in enumerate(roles):
                Judge.objects.create(tribunal=tribunal, user=teachers[idx], role=role)

            self.stdout.write(self.style.SUCCESS(f"✅ Created Tribunal for TFM: {tfm.title}"))
