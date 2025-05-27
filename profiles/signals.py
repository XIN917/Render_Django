from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile
from institutions.models import Institution  # Import your Institution model

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = Profile.objects.get_or_create(user=instance)
        if instance.role == 'teacher' and not profile.institution:
            # Assign a default institution, e.g., the first one in the database
            default_institution = Institution.objects.first()
            if default_institution:
                profile.institution = default_institution
                profile.save()
