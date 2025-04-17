from django.db import models
from tfms.models import TFM
from slots.models import Slot
from users.models import User
from judges.models import Judge

class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    judges = models.ManyToManyField(User, through='judges.Judge', related_name='tribunals')

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"

    def add_judge(self, user: User, role: str):
        """
        Helper method to add a judge with a role.
        """
        return Judge.objects.create(tribunal=self, user=user, role=role)
