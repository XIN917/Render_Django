from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Seed default admin, teachers, and students"

    def handle(self, *args, **kwargs):
        users_to_create = [
            {
                "email": "admin@email.com",
                "password": "admin1234",
                "full_name": "Admin User",
                "role": "teacher",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "email": "teacher1@example.com",
                "password": "12345678",
                "full_name": "Dr. John Director",
                "role": "teacher",
            },
            {
                "email": "teacher2@example.com",
                "password": "12345678",
                "full_name": "Dr. Jane Director",
                "role": "teacher",
            },
            {
                "email": "student1@example.com",
                "password": "12345678",
                "full_name": "Alice Student",
                "role": "student",
            },
            {
                "email": "student2@example.com",
                "password": "12345678",
                "full_name": "Bob Student",
                "role": "student",
            },
        ]

        for data in users_to_create:
            if not User.objects.filter(email=data["email"]).exists():
                user = User.objects.create_user(
                    email=data["email"],
                    password=data["password"],
                    full_name=data["full_name"],
                    role=data["role"],
                )
                user.is_staff = data.get("is_staff", False)
                user.is_superuser = data.get("is_superuser", False)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {user.email}"))
            else:
                self.stdout.write(f"⚠️  User already exists: {data['email']}")
