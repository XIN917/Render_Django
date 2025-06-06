from django.core.management.base import BaseCommand
from tfms.models import TFM
from users.models import User
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from io import BytesIO
import random

class Command(BaseCommand):
    help = "Seed 50 TFMs with generic titles and random directors"

    def handle(self, *args, **kwargs):
        students = list(User.objects.filter(role="student"))
        teachers = list(User.objects.filter(role="teacher"))

        if not students:
            self.stdout.write(self.style.ERROR("No students found"))
            return
        if len(teachers) < 2:
            self.stdout.write(self.style.ERROR("At least 2 teachers required to assign directors"))
            return

        created_count = 0

        for i in range(1, 51):
            title = f"TFM Project {i}"
            if TFM.objects.filter(title=title).exists():
                continue

            student = students[i % len(students)]
            directors = random.sample(teachers, k=random.randint(1, 2))

            # Create dummy PDF
            buffer = BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 750, f"This is the PDF for {title}")
            p.save()
            pdf_file = ContentFile(buffer.getvalue(), name=f"{title.replace(' ', '_')}.pdf")

            tfm = TFM.objects.create(
                title=title,
                description=f"Description for {title}",
                author=student,
            )
            tfm.file.save(f"{title.replace(' ', '_')}.pdf", pdf_file, save=True)
            tfm.directors.set(directors)
            tfm.save()

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_count} TFMs"))
