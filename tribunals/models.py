from django.db import models
from tfms.models import TFM
from slots.models import Slot
from users.models import User


class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='TribunalMember')

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"

class TribunalMember(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('secretary', 'Secretary'),
        ('vocal', 'Vocal'),
    ]

    tribunal = models.ForeignKey(Tribunal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = (
            ('tribunal', 'user'),  # Each user can only be in a tribunal once
        )

    def __str__(self):
        return f"{self.user.get_full_name()} as {self.get_role_display()} in {self.tribunal}"
