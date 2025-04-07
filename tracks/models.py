from django.db import models
from slots.models import Slot

class Track(models.Model):
    title = models.CharField(max_length=100)
    slots = models.ManyToManyField(Slot)

    def __str__(self):
        return self.title
