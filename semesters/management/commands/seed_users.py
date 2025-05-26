from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from institutions.models import Institution

User = get_user_model()

class Command(BaseCommand):
    help = "Seed default admin, teachers, and students"

    def handle(self, *args, **kwargs):
        # Admin user
        if not User.objects.filter(email="admin@email.com").exists():
            User.objects.create_superuser(
                email="admin@email.com",
                full_name="Admin User",
                password="admin1234",
                role=User.TEACHER,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS("✅ Created admin user"))
        else:
            self.stdout.write("⚠️ Admin user already exists")

        # Get all institutions to assign teachers
        institutions = list(Institution.objects.all())
        if not institutions:
            self.stdout.write(self.style.WARNING("⚠️ No institutions found. Please create at least one institution before seeding teachers."))
            return

        # Teachers
        for i in range(1, 21):
            email = f"teacher{i}@example.com"
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    full_name=f"Dr. Teacher {i}",
                    role=User.TEACHER,
                    password="pass1234"
                )
                # Assign institution to profile (random or cycle)
                institution = institutions[(i - 1) % len(institutions)]
                profile, created = user.profile.__class__.objects.get_or_create(user=user)
                profile.institution = institution
                profile.save()

                self.stdout.write(self.style.SUCCESS(f"✅ Created {email} with institution {institution.name}"))

        # Students
        for i in range(1, 21):
            email = f"student{i}@example.com"
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    full_name=f"Student {i}",
                    role=User.STUDENT,
                    password="pass1234"
                )
                self.stdout.write(self.style.SUCCESS(f"✅ Created {email}"))
