#!/bin/bash
set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Seed data
python manage.py seed_all

# Check if CREATE_SUPERUSER is set and not empty
if [[ -n "$CREATE_SUPERUSER" ]]; then
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
full_name = os.getenv("DJANGO_SUPERUSER_FULL_NAME")

if email and password and full_name:
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(
            email=email,
            password=password,
            full_name=full_name
        )
        print("✅ Superuser created successfully")
    else:
        print("⚠️ Superuser already exists")
else:
    print("❌ Missing environment variables for superuser creation")
EOF
fi