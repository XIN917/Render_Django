#!/bin/bash
set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Delete all existing data before seeding
# python manage.py delete_all_data

# Seed data
python manage.py seed_all
