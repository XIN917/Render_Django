from django.db import models
from datetime import timedelta
from config.models import PresentationDay
from tracks.models import Track  # Assuming app name is 'tracks'

class Slot(models.Model):
    presentation_day = models.ForeignKey(PresentationDay, on_delete=models.CASCADE, default=PresentationDay.get_or_create_singleton)
    start_time = models.TimeField()
    end_time = models.TimeField()
    tfm_duration = models.DurationField(default=timedelta(minutes=45))
    max_tfms = models.PositiveIntegerField(default=2)
    room = models.CharField(max_length=100)
    
    track = models.ForeignKey('tracks.Track', on_delete=models.SET_NULL, null=True, blank=True, related_name='slots')

    def is_full(self):
        return self.tribunals.count() >= self.max_tfms

    def __str__(self):
        return f"{self.presentation_day.date} | {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} in Room {self.room}"

    def get_tfms(self):
        return [tribunal.tfm for tribunal in self.tribunals.select_related('tfm') if tribunal.tfm]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
