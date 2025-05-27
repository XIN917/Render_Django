from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Delete all data from only the models seeded by seed_all. Use with caution!"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️ Deleting all data from selected models..."))
        # List of app_label.model_name to delete, in dependency-safe order
        models_to_delete = [
            ('institutions', 'Institution'),
            ('semesters', 'Semester'),
            ('users', 'User'),
            ('tracks', 'Track'),
            ('slots', 'Slot'),
            ('tfms', 'TFM'),
            ('tribunals', 'Tribunal'),
        ]
        for app_label, model_name in models_to_delete:
            try:
                model = apps.get_model(app_label, model_name)
                deleted, _ = model.objects.all().delete()
                self.stdout.write(self.style.NOTICE(f"Deleted {deleted} objects from {app_label}.{model_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting from {app_label}.{model_name}: {e}"))
        self.stdout.write(self.style.SUCCESS("✅ Selected data deleted."))
