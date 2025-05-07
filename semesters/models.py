from django.db import models

class Semester(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    presentation_day = models.DateField()
    min_judges = models.PositiveIntegerField(default=3)
    max_judges = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name
