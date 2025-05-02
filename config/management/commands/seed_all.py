from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    help = "Seed the full database: users, semesters, institutions, tracks, slots, TFMs, tribunals"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("🚀 Starting full data seed..."))

        # Core data
        management.call_command("seed_users")
        management.call_command("seed_institutions")
        management.call_command("seed_semesters")

        # Structure
        management.call_command("seed_slots")
        management.call_command("seed_tracks")

        # Content
        management.call_command("seed_tfms")
        management.call_command("seed_tribunals")

        self.stdout.write(self.style.SUCCESS("✅ All data successfully seeded."))
