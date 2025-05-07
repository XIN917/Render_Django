from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class PresentationDay(models.Model):
    date = models.DateField()

    def save(self, *args, **kwargs):
        # Enforce singleton: only one instance allowed
        if not self.pk and PresentationDay.objects.exists():
            raise ValidationError("Only one PresentationDay instance is allowed.")
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create_singleton(cls, default_date=None):
        """
        Returns the existing PresentationDay or creates one with the given default date.
        :param default_date: datetime.date, optional (defaults to June 15, 2025)
        """
        instance = cls.objects.first()
        if instance:
            return instance

        default_date = default_date or date(2025, 6, 15)

        try:
            return cls.objects.create(date=default_date)
        except ValidationError:
            return cls.objects.first()

    def __str__(self):
        return f"Presentation Day: {self.date}"

    class Meta:
        verbose_name = "Presentation Day"
        verbose_name_plural = "Presentation Day"
