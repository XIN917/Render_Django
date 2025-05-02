from django.core.management.base import BaseCommand
from tfms.models import TFM
from users.models import User
from slots.models import Slot
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import random

class Command(BaseCommand):
    help = "Seed TFMs linked to all available slots across semesters"

    def generate_pdf_bytes(self, title: str) -> bytes:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("Helvetica", 18)
        c.drawString(100, 750, f"TFM Project: {title}")
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, "Generated as part of the seeding process.")
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer.read()

    def handle(self, *args, **kwargs):
        students = list(User.objects.filter(role="student"))
        teachers = list(User.objects.filter(role="teacher", is_superuser=False))
        slots = Slot.objects.all().order_by("start_time")

        titles = [
            "AI for Predictive Healthcare", "Blockchain Voting Systems",
            "Smart Grid Optimization", "Legal NLP Assistants",
            "Satellite Image Analysis", "IoT Security Architecture",
            "Climate Data Visualization", "Digital Twin Systems",
            "Disease Risk Prediction", "Smart Mobility Solutions",
            "Federated Edge Learning", "Finance Automation AI",
            "ML Privacy Preserving", "Student Grade Forecasting",
            "Encrypted Chat Protocol", "Elder Care Monitoring",
            "Contract Auto-Audit", "ID Systems for E-Gov",
            "Green Cloud Engines", "Virtual OR Training"
        ]

        for i, slot in enumerate(slots):
            title = titles[i % len(titles)] + f" ({slot.id})"
            if TFM.objects.filter(title=title).exists():
                continue

            student = students[i % len(students)]
            directors = random.sample(teachers, k=random.randint(1, 2))
            tfm = TFM.objects.create(
                title=title,
                description="A detailed exploration of " + title.lower(),
                file=ContentFile(self.generate_pdf_bytes(title), name=f"tfm_{i+1}.pdf"),
                student=student
            )
            tfm.directors.set(directors)
            tfm.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created TFM: {title}"))
