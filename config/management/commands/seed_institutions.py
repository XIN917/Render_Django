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

        institutions_to_create = [
            Institution(name=uni["name"], city=uni["city"])
            for uni in universities
            if not Institution.objects.filter(name=uni["name"]).exists()
        ]

        if institutions_to_create:
            Institution.objects.bulk_create(institutions_to_create)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(institutions_to_create)} institutions"))
        else:
            self.stdout.write("⚠️ All institutions already exist")