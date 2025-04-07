from django.db import models
from django.core.exceptions import ValidationError

class PresentationDay(models.Model):
    date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.pk and PresentationDay.objects.exists():
            raise ValidationError("Only one PresentationDay instance is allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Presentation Day: {self.date}"

    class Meta:
        verbose_name = "Presentation Day"
        verbose_name_plural = "Presentation Day"
