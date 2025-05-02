from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Seed default admin, teachers, and students"

    def handle(self, *args, **kwargs):
        # Admin user
        if not User.objects.filter(email="admin@email.com").exists():
            admin = User.objects.create_user(
                email="admin@email.com",
                full_name="Admin User",
                role="teacher",
                password="admin1234",
                is_staff=True,
                is_superuser=True,
            )
            admin.save()
            self.stdout.write(self.style.SUCCESS("✅ Created admin user"))

        # Teachers
        for i in range(1, 21):
            email = f"teacher{i}@example.com"
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    full_name=f"Dr. Teacher {i}",
                    role="teacher",
                    password="pass1234"
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {email}"))
            else:
                self.stdout.write(f"⚠️  Teacher already exists: {email}")

        # Students
        for i in range(1, 21):
            email = f"student{i}@example.com"
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    full_name=f"Student {i}",
                    role="student",
                    password="pass1234"
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {email}"))
            else:
                self.stdout.write(f"⚠️  Student already exists: {email}")
