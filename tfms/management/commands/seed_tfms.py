from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from tfms.models import Director, TFM
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with sample TFMs, users, and directors"

    def handle(self, *args, **kwargs):
        # 🧹 Borrar datos existentes
        TFM.objects.all().delete()
        Director.objects.all().delete()
        User.objects.filter(email__in=[
            "student1@example.com",
            "student2@example.com",
            "teacher1@example.com",
            "teacher2@example.com",
        ]).delete()

        self.stdout.write("🧹 Previous sample TFMs, directors and users deleted.")

        # 1. Crear estudiantes
        student1 = User.objects.create_user(
            email="student1@example.com",
            full_name="Alice Student",
            password="password123",
            role="student"
        )

        student2 = User.objects.create_user(
            email="student2@example.com",
            full_name="Bob Student",
            password="password123",
            role="student"
        )

        # 2. Crear profesores y directores
        teacher1 = User.objects.create_user(
            email="teacher1@example.com",
            full_name="Dr. John Director",
            password="password123",
            role="teacher",
            is_staff=True
        )

        teacher2 = User.objects.create_user(
            email="teacher2@example.com",
            full_name="Dr. Jane Director",
            password="password123",
            role="teacher",
            is_staff=True
        )

        director1 = Director.objects.create(user=teacher1)
        director2 = Director.objects.create(user=teacher2)

        # 3. Crear TFMs (ensure uniqueness by checking title+student+directors)
        try:
            tfm1 = TFM.objects.create(
                title="AI in Medical Imaging",
                description="Using deep learning to assist diagnosis.",
                file=ContentFile(b"PDF content for TFM 1", name="ai_medical.pdf"),
                student=student1
            )
            tfm1.directors.add(director1)
        except IntegrityError:
            self.stdout.write(self.style.WARNING("⚠️  TFM 1 already exists and was skipped."))

        try:
            tfm2 = TFM.objects.create(
                title="Blockchain for Education Records",
                description="A secure ledger for academic credentials.",
                file=ContentFile(b"PDF content for TFM 2", name="blockchain_edu.pdf"),
                student=student2
            )
            tfm2.directors.set([director1, director2])
        except IntegrityError:
            self.stdout.write(self.style.WARNING("⚠️  TFM 2 already exists and was skipped."))

        self.stdout.write(self.style.SUCCESS("✅ Sample TFMs, students, and directors created!"))
