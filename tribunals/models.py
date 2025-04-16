from django.db import models
from tfms.models import TFM
from slots.models import Slot
from users.models import User


class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    president = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tribunal_president')
    secretary = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tribunal_secretary')
    vocals = models.ManyToManyField(User, related_name='tribunal_vocals')

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"