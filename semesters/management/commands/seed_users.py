from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from institutions.models import Institution

User = get_user_model()

class Command(BaseCommand):
    help = "Seed default admin, teachers, and students"

    def handle(self, *args, **kwargs):
        created_teachers = 0
        created_students = 0

        institutions = list(Institution.objects.all())
        if not institutions:
            self.stdout.write(self.style.WARNING("⚠️ No institutions found. Please create at least one institution before seeding users."))
            return

        # Select the second institution (UB expected)
        if len(institutions) >= 2:
            admin_institution = institutions[1]
        else:
            self.stdout.write(self.style.WARNING("⚠️ Less than 2 institutions found. Admin won't be assigned an institution."))
            admin_institution = None

        # Admin user
        if not User.objects.filter(email="admin@email.com").exists():
            admin = User.objects.create_superuser(
                email="admin@email.com",
                full_name="Admin User",
                password="admin1234",
                role=User.TEACHER,
                is_staff=True,
                is_superuser=True,
            )
            if admin_institution:
                profile, _ = admin.profile.__class__.objects.get_or_create(user=admin)
                profile.institution = admin_institution
                profile.save()
            self.stdout.write(self.style.SUCCESS("✅ Created admin user"))
        else:
            self.stdout.write("⚠️ Admin user already exists")

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
                institution = institutions[(i - 1) % len(institutions)]
                profile, _ = user.profile.__class__.objects.get_or_create(user=user)
                profile.institution = institution
                profile.save()
                created_teachers += 1

        # Students
        for i in range(1, 51):
            email = f"student{i}@example.com"
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    full_name=f"Student {i}",
                    role=User.STUDENT,
                    password="pass1234"
                )
                created_students += 1

        # Final summary
        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_teachers} teachers"))
        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_students} students"))
