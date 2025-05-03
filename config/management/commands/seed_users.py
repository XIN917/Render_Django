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
        else:
            self.stdout.write("⚠️ Admin user already exists")

        # Teachers
        teachers_to_create = []
        for i in range(1, 21):
            email = f"teacher{i}@example.com"
            if not User.objects.filter(email=email).exists():
                teachers_to_create.append(User(
                    email=email,
                    full_name=f"Dr. Teacher {i}",
                    role="teacher",
                    password="pass1234"
                ))

        if teachers_to_create:
            User.objects.bulk_create(teachers_to_create)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(teachers_to_create)} teachers"))
        else:
            self.stdout.write("⚠️ All teachers already exist")

        # Students
        students_to_create = []
        for i in range(1, 21):
            email = f"student{i}@example.com"
            if not User.objects.filter(email=email).exists():
                students_to_create.append(User(
                    email=email,
                    full_name=f"Student {i}",
                    role="student",
                    password="pass1234"
                ))

        if students_to_create:
            User.objects.bulk_create(students_to_create)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(students_to_create)} students"))
        else:
            self.stdout.write("⚠️ All students already exist")