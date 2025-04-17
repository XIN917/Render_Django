from django.db import models
from datetime import timedelta
from tfms.models import TFM
from config.models import PresentationDay


class Slot(models.Model):
    presentation_day = models.ForeignKey(PresentationDay, on_delete=models.CASCADE, default=PresentationDay.get_or_create_singleton)
    start_time = models.TimeField()
    end_time = models.TimeField()
    tfm_duration = models.DurationField(default=timedelta(minutes=45))
    max_tfms = models.PositiveIntegerField(default=2)
    tfms = models.ManyToManyField(TFM, blank=True)
    room = models.CharField(max_length=100)

    def is_full(self):
        return self.tfms.count() >= self.max_tfms

    def __str__(self):
        return f"{self.presentation_day.date} | {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} in Room {self.room}"
