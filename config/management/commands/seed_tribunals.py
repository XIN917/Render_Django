from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from tfms.models import TFM
from slots.models import Slot
from users.models import User
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = "Seed test tribunals"

    def handle(self, *args, **kwargs):
        Tribunal.objects.all().delete()

        tfms = TFM.objects.all()
        slots = Slot.objects.all()
        teachers = User.objects.filter(role='teacher')

        if teachers.count() < 4 or tfms.count() == 0:
            self.stdout.write(self.style.WARNING("Not enough data to seed tribunals"))
            return

        for i, tfm in enumerate(tfms[:len(slots)]):
            slot = slots[i]
            president = teachers[0]
            secretary = teachers[1]
            vocals = teachers[2:4]  # Make sure these aren't president/secretary

            tribunal = Tribunal(
                tfm=tfm,
                slot=slot,
                president=president,
                secretary=secretary
            )
            tribunal.save()
            tribunal.vocals.set(vocals)

            try:
                tribunal.clean_roles()  # Validate after M2M set
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f"❌ Invalid tribunal for {tfm.title}: {e.messages[0]}"))
                tribunal.delete()  # Optional: cleanup invalid entry
            else:
                self.stdout.write(self.style.SUCCESS(f"✅ Created Tribunal for {tfm.title}"))
