from django.core.management.base import BaseCommand
from institutions.models import Institution

class Command(BaseCommand):
    help = "Seed core Catalan universities into the Institution table."

    def handle(self, *args, **kwargs):
        universities = [
            {"name": "UAB", "city": "Cerdanyola del Vallès"},
            {"name": "UB", "city": "Barcelona"},
            {"name": "UPF", "city": "Barcelona"},
            {"name": "UPC", "city": "Barcelona"},
            {"name": "UOC", "city": "Barcelona"},
        ]

        for uni in universities:
            obj, created = Institution.objects.get_or_create(name=uni["name"], defaults={"city": uni["city"]})
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {obj.name}"))
            else:
                self.stdout.write(f"⚠️ Already exists: {obj.name}")
