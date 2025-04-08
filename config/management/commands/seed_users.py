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
                "full_name": "Dr. John Director",
                "password": "password123",
                "role": "teacher"
            },
            {
                "email": "teacher2@example.com",
                "full_name": "Dr. Jane Director",
                "password": "password123",
                "role": "teacher"
            },
            {
                "email": "teacher3@example.com",
                "full_name": "Dr. Clara Mentor",
                "role": "teacher"
            },
            {
                "email": "teacher4@example.com",
                "full_name": "Dr. Mike Supervisor",
                "role": "teacher"
            },
            {
                "email": "teacher5@example.com",
                "full_name": "Dr. Emma Advisor",
                "role": "teacher"
            },
            {
                "email": "student1@example.com",
                "full_name": "Alice Student",
                "password": "password123",
                "role": "student"
            },
            {
                "email": "student2@example.com",
                "full_name": "Bob Student",
                "password": "password123",
                "role": "student"
            },
            {
                "email": "student3@example.com",
                "full_name": "Charlie Learner",
                "role": "student"
            },
            {
                "email": "student4@example.com",
                "full_name": "Diana Researcher",
                "role": "student"
            },
            {
                "email": "student5@example.com",
                "full_name": "Ethan Scholar",
                "role": "student"
            },
        ]

        for data in users_to_create:
            if User.objects.filter(email=data["email"]).exists():
                self.stdout.write(f"⚠️  User already exists: {data['email']}")
                continue

            create_kwargs = {
                "email": data["email"],
                "full_name": data["full_name"],
                "role": data["role"],
                "password": data.get("password"),
            }

            user = User.objects.create_user(**create_kwargs)
            user.is_staff = data.get("is_staff", False)
            user.is_superuser = data.get("is_superuser", False)
            user.save()

            self.stdout.write(self.style.SUCCESS(f"✅ Created: {user.email}"))

