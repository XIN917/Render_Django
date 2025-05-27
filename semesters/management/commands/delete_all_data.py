from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Delete all data from all models in the database. Use with caution!"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️ Deleting all data from all models..."))
        models = apps.get_models()
        for model in models:
            model_name = model.__name__
            try:
                deleted, _ = model.objects.all().delete()
                self.stdout.write(self.style.NOTICE(f"Deleted {deleted} objects from {model_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting from {model_name}: {e}"))
        self.stdout.write(self.style.SUCCESS("✅ All data deleted."))
