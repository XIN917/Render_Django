from django.db import models

class Semester(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    presentation_day = models.DateField()

    def __str__(self):
        return self.name
