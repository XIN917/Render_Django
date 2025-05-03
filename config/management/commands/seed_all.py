from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    help = "Seed the full database: users, semesters, institutions, tracks, slots, TFMs, tribunals"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("🚀 Starting full data seed..."))

        self.stdout.write(self.style.NOTICE("📦 Seeding users..."))
        management.call_command("seed_users")

        self.stdout.write(self.style.NOTICE("🏛️ Seeding institutions..."))
        management.call_command("seed_institutions")

        self.stdout.write(self.style.NOTICE("📅 Seeding semesters..."))
        management.call_command("seed_semesters")

        self.stdout.write(self.style.NOTICE("📚 Seeding slots..."))
        management.call_command("seed_slots")

        self.stdout.write(self.style.NOTICE("📊 Seeding tracks..."))
        management.call_command("seed_tracks")

        self.stdout.write(self.style.NOTICE("📝 Seeding TFMs..."))
        management.call_command("seed_tfms")

        self.stdout.write(self.style.NOTICE("🏛️ Seeding tribunals..."))
        management.call_command("seed_tribunals")

        self.stdout.write(self.style.SUCCESS("✅ All data successfully seeded."))
