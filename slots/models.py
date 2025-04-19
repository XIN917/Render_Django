from django.db import models
from datetime import timedelta
from config.models import PresentationDay

class Slot(models.Model):
    presentation_day = models.ForeignKey(PresentationDay, on_delete=models.CASCADE, default=PresentationDay.get_or_create_singleton)
    start_time = models.TimeField()
    end_time = models.TimeField()
    tfm_duration = models.DurationField(default=timedelta(minutes=45))
    max_tfms = models.PositiveIntegerField(default=2)
    room = models.CharField(max_length=100)

    def is_full(self):
        return self.tribunals.count() >= self.max_tfms

    def __str__(self):
        return f"{self.presentation_day.date} | {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} in Room {self.room}"

    def get_tfms(self):
        return [tribunal.tfm for tribunal in self.tribunals.select_related('tfm') if tribunal.tfm]
    
    def save(self, *args, **kwargs):
        if self.start_time and self.max_tfms and self.tfm_duration:
            from datetime import datetime
            start_dt = datetime.combine(datetime.today(), self.start_time)
            self.end_time = (start_dt + self.tfm_duration * self.max_tfms).time()
        super().save(*args, **kwargs)
