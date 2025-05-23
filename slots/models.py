from django.db import models
from datetime import date
from tracks.models import Track
from django.core.exceptions import ValidationError

class Slot(models.Model):
    date = models.DateField()  # The specific day this slot is scheduled

    start_time = models.TimeField()
    end_time = models.TimeField()
    max_tfms = models.PositiveIntegerField(default=2)
    room = models.CharField(max_length=100)

    track = models.ForeignKey('tracks.Track', on_delete=models.SET_NULL, null=True, blank=True, related_name='slots')

    def is_full(self):
        return self.tribunals.count() >= self.max_tfms

    def get_tfms(self):
        return [tribunal.tfm for tribunal in self.tribunals.select_related('tfm') if tribunal.tfm]

    def clean(self):
        # Ensure track and semester are defined
        if not self.track or not self.track.semester:
            raise ValidationError("Slot must be linked to a track with an active semester.")

        semester = self.track.semester

        # Check date is in allowed presentation window
        if not (semester.int_presentation_date <= self.date <= semester.last_presentation_date):
            raise ValidationError("Slot date must be within the allowed presentation period.")

        # Ensure date is a weekday
        if self.date.weekday() >= 5:
            raise ValidationError("Slot date cannot fall on a weekend.")

        # Check time is within daily bounds
        if self.start_time < semester.daily_start_time:
            raise ValidationError("Slot start time is before the allowed daily presentation start time.")
        if self.end_time > semester.daily_end_time:
            raise ValidationError("Slot end time is after the allowed daily presentation end time.")
        if self.end_time <= self.start_time:
            raise ValidationError("Slot end time must be after the start time.")

        # Check if total duration can fit all TFMs
        duration = semester.pre_duration
        total_required_time = duration * self.max_tfms
        actual_slot_seconds = (
            (self.end_time.hour * 60 + self.end_time.minute) -
            (self.start_time.hour * 60 + self.start_time.minute)
        ) * 60

        if total_required_time.total_seconds() > actual_slot_seconds:
            raise ValidationError("Slot does not have enough time to accommodate all TFMs based on the standard duration.")
        
        # ✅ Check for time overlap in the same room and date
        overlapping = Slot.objects.filter(
            date=self.date,
            room=self.room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("This slot overlaps with another slot in the same room and date.")

    def __str__(self):
        return f"{self.date} | {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} in Room {self.room}"
