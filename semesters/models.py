from django.db import models
from django.core.exceptions import ValidationError
from datetime import time, timedelta

class Semester(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    # Presentation date range
    int_presentation_date = models.DateField()   # initial presentation day
    last_presentation_date = models.DateField()  # final presentation day

    # Daily time window
    daily_start_time = models.TimeField(default=time(10, 0))  # earliest possible start
    daily_end_time = models.TimeField(default=time(19, 0))    # latest possible end

    # Standard duration for each presentation
    pre_duration = models.DurationField(default=timedelta(minutes=45))

    # Tribunal rules
    min_committees = models.PositiveIntegerField(default=3)
    max_committees = models.PositiveIntegerField(default=5)

    def clean(self):
        # Presentation range must be valid
        if self.int_presentation_date >= self.last_presentation_date:
            raise ValidationError("Initial presentation date must be strictly before the last presentation date.")

        # Semester date range must be valid
        if self.start_date >= self.end_date:
            raise ValidationError("Semester start date must be strictly before the end date.")

        # Weekday check for presentation dates
        if self.int_presentation_date.weekday() >= 5:
            raise ValidationError({'int_presentation_date': "Initial presentation date cannot be on a weekend."})
        if self.last_presentation_date.weekday() >= 5:
            raise ValidationError({'last_presentation_date': "Last presentation date cannot be on a weekend."})

        # Weekday check for semester start and end dates
        if self.start_date.weekday() >= 5:
            raise ValidationError({'start_date': "Semester start date cannot be on a weekend."})
        if self.end_date.weekday() >= 5:
            raise ValidationError({'end_date': "Semester end date cannot be on a weekend."})

    def __str__(self):
        return self.name
