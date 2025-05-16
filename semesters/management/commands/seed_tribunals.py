from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from tfms.models import TFM
from users.models import User
from slots.models import Slot
from committees.models import Committee
from semesters.models import Semester  # Import Semester model
from datetime import date
import random

class Command(BaseCommand):
    help = "Seed tribunals and assign committees"

    def handle(self, *args, **kwargs):
        tfms = list(TFM.objects.all())
        teachers = list(User.objects.filter(role="teacher", is_superuser=False, is_staff=False))

        # Get the most recent past semester and the current semester
        past_semester = Semester.objects.filter(end_date__lt=date.today()).order_by('-end_date').first()
        current_semester = Semester.objects.filter(start_date__lte=date.today(), end_date__gte=date.today()).first()

        if not past_semester or not current_semester:
            self.stdout.write(self.style.ERROR("❌ Could not find past or current semester"))
            return

        # Filter slots by semester
        past_slots = list(Slot.objects.filter(track__semester=past_semester, tribunals__isnull=True))
        current_slots = list(Slot.objects.filter(track__semester=current_semester, tribunals__isnull=True))

        if not past_slots and not current_slots:
            self.stdout.write(self.style.WARNING("⚠️ No available slots for tribunal assignment"))
            return

        if not teachers:
            self.stdout.write(self.style.ERROR("❌ No teachers available for tribunal assignment"))
            return

        tribunals_to_create = []
        committees_to_create = []

        for i, tfm in enumerate(tfms):
            if Tribunal.objects.filter(tfm=tfm).exists():
                self.stdout.write(self.style.WARNING(f"⚠️ Tribunal already exists for TFM: {tfm.title}"))
                continue

            # Alternate between past and current slots
            available_slots = past_slots if i % 2 == 0 else current_slots
            available_slots = [s for s in available_slots if not s.is_full()]
            if not available_slots:
                self.stdout.write(self.style.WARNING(f"ℹ️ No available slots to assign TFM '{tfm.title}'"))
                continue

            slot = available_slots[i % len(available_slots)]
            tribunal = Tribunal(tfm=tfm, slot=slot)
            tribunals_to_create.append(tribunal)

            # Assign committees
            committees = random.sample(teachers, k=3)
            roles = ["president", "secretary", "vocal"]
            for user, role in zip(committees, roles):
                committees_to_create.append(Committee(tribunal=tribunal, user=user, role=role))

        # Bulk create tribunals and committees
        Tribunal.objects.bulk_create(tribunals_to_create)
        Committee.objects.bulk_create(committees_to_create)

        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(tribunals_to_create)} tribunals"))