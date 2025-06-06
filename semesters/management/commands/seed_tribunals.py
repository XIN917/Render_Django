from django.core.management.base import BaseCommand
from tribunals.models import Tribunal
from tfms.models import TFM
from users.models import User
from slots.models import Slot
from committees.models import Committee
from semesters.models import Semester
from datetime import date
import random

class Command(BaseCommand):
    help = "Seed one tribunal per TFM and assign a 3-member committee"

    def handle(self, *args, **kwargs):
        tfms = list(TFM.objects.all())
        teachers = list(User.objects.filter(role="teacher"))

        past_semester = Semester.objects.filter(end_date__lt=date.today()).order_by('-end_date').first()
        current_semester = Semester.objects.filter(start_date__lte=date.today(), end_date__gte=date.today()).first()

        if not past_semester or not current_semester:
            self.stdout.write(self.style.ERROR("❌ Missing past or current semester"))
            return

        # Gather and shuffle all available slots across both semesters
        all_slots = list(Slot.objects.filter(
            track__semester__in=[past_semester, current_semester],
            tribunals__isnull=True
        ))
        all_slots = [s for s in all_slots if not s.is_full()]
        random.shuffle(all_slots)  # Shuffle to spread across tracks

        if not all_slots:
            self.stdout.write(self.style.WARNING("⚠️ No available slots"))
            return

        if len(teachers) < 3:
            self.stdout.write(self.style.ERROR("❌ At least 3 teachers required"))
            return

        created_tribunals = 0
        for tfm in tfms:
            if Tribunal.objects.filter(tfm=tfm).exists():
                continue

            while all_slots:
                slot = all_slots.pop()
                if not slot.is_full():
                    break
            else:
                self.stdout.write("⚠️ Ran out of available slots")
                break

            tribunal = Tribunal.objects.create(tfm=tfm, slot=slot)
            committee_members = random.sample(teachers, 3)
            roles = ["president", "secretary", "vocal"]

            Committee.objects.bulk_create([
                Committee(tribunal=tribunal, user=user, role=role)
                for user, role in zip(committee_members, roles)
            ])

            created_tribunals += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_tribunals} tribunals"))
