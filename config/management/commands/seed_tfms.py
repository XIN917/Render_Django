# seed_tfms.py

from django.core.management.base import BaseCommand
from tfms.models import TFM
from users.models import User
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from io import BytesIO
import random

class Command(BaseCommand):
    help = "Seed TFMs with sample data"

    def handle(self, *args, **kwargs):
        students = list(User.objects.filter(role="student"))
        teachers = list(User.objects.filter(role="teacher", is_superuser=False, is_staff=False))

        tfm_titles = [
            "AI in Medical Imaging",
            "Blockchain for Education Records",
            "TFM01",
            "TFM02",
            "TFM03",
            "Sustainable Agriculture with IoT",
            "Neural Interfaces for Prosthetics",
            "Mobile Health Monitoring",
            "Cyber Threat Detection System",
            "Smart Grid Optimization",
            "Digital Twins in Manufacturing",
            "Ethical AI Decision-Making",
            "AR for Virtual Labs",
            "Energy Harvesting Sensors",
            "Secure Voting via Blockchain",
            "Assistive Robotics",
            "Green Cloud Computing",
            "AI-Powered Legal Assistants",
            "Quantum Secure Messaging",
            "Autonomous Drone Navigation"
        ]

        for i, title in enumerate(tfm_titles):
            if TFM.objects.filter(title=title).exists():
                self.stdout.write(self.style.WARNING(f"⚠️ TFM already exists: {title}"))
                continue

            student = students[i % len(students)]
            directors = random.sample(teachers, k=random.randint(1, 2))

            # Generate a PDF file
            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 750, f"This is the PDF for {title}")
            p.save()
            pdf_file = ContentFile(buffer.getvalue(), name=f"{title.replace(' ', '_')}.pdf")

            tfm = TFM.objects.create(
                title=title,
                description=f"Description for {title}",
                student=student,
                file=pdf_file,
            )
            tfm.directors.set(directors)
            tfm.save()

            self.stdout.write(self.style.SUCCESS(f"✅ Created TFM: {title}"))
