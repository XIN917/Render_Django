from django.db import models
from django.core.exceptions import ValidationError
from tfms.models import TFM
from slots.models import Slot
from users.models import User


class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    president = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tribunal_president')
    secretary = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tribunal_secretary')
    vocals = models.ManyToManyField(User, related_name='tribunal_vocals')

    def clean(self):
        roles = {self.president, self.secretary}
        if roles & set(self.vocals.all()):
            raise ValidationError("A judge cannot hold more than one role in a tribunal.")
        if len(self.vocals.all()) < 1:
            raise ValidationError("At least one vocal is required.")

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

        if self.tfm and self.slot:
            self.slot.tfms.add(self.tfm)