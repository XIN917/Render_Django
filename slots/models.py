from django.db import models
from datetime import time, timedelta
from django.core.exceptions import ValidationError
from tfms.models import TFM


class Slot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    tfm_duration = models.DurationField(default=timedelta(minutes=45))
    tfms = models.ManyToManyField(TFM, blank=True)

    def clean(self):
        if self.start_time.minute not in (0, 30) or self.end_time.minute not in (0, 30):
            raise ValidationError("Time must be on the hour or half-hour.")
        if self.start_time < time(8, 0) or self.end_time > time(21, 0):
            raise ValidationError("Slot time must be between 08:00 and 21:00.")
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
