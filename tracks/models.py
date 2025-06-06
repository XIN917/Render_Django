from django.db import models
from semesters.models import Semester

class Track(models.Model):
    title = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT)

    def __str__(self):
        return self.title
