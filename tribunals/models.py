from django.db import models
from django.core.exceptions import ValidationError
from tfms.models import TFM
from slots.models import Slot
from users.models import User


class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    president = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tribunal_president')
    secretary = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tribunal_secretary')
    vocals = models.ManyToManyField(User, related_name='tribunal_vocals')

    def clean(self):
        # Validate president and secretary
        if self.president == self.secretary:
            raise ValidationError("President and secretary must be different.")
        if self.president.is_superuser or self.secretary.is_superuser:
            raise ValidationError("Superusers cannot be assigned as president or secretary.")

    def clean_roles(self):
        """Call this after vocals are assigned."""
        roles = {self.president, self.secretary}
        if roles & set(self.vocals.all()):
            raise ValidationError("A judge cannot hold more than one role in a tribunal.")
        if self.vocals.count() < 1:
            raise ValidationError("At least one vocal is required.")
        if any(vocal.is_superuser for vocal in self.vocals.all()):
            raise ValidationError("Superusers cannot be assigned as vocals.")

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"

    def save(self, *args, **kwargs):
        self.clean()  # Only basic field validation
        super().save(*args, **kwargs)

        if self.tfm and self.slot:
            self.slot.tfms.add(self.tfm)