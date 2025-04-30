from django.db import models
from tfms.models import TFM
from slots.models import Slot
from users.models import User
from judges.models import Judge

MIN_JUDGES = 3
MAX_JUDGES = 5

class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE, unique=True)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='tribunals')
    judges = models.ManyToManyField(User, through='judges.Judge', related_name='tribunals')
    index = models.IntegerField(default=0)

    class Meta:
        unique_together = (('slot', 'index'),)

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            existing_indexes = list(self.slot.tribunals.values_list('index', flat=True))
            if len(existing_indexes) >= self.slot.max_tfms:
                raise ValueError(f"Slot '{self.slot}' has reached its maximum number of TFMs.")

            if self.index == 0 and 0 in existing_indexes:
                # Assign next available index if 0 is taken
                next_index = 0
                while next_index in existing_indexes:
                    next_index += 1
                self.index = next_index

        super().save(*args, **kwargs)

    def add_judge(self, user: User, role: str):
        """Helper method to add a judge with a role."""
        return Judge.objects.create(tribunal=self, user=user, role=role)
    
    def is_ready(self):
        """Check if the tribunal is ready (i.e., has all judges assigned)."""
        return self.judges.count() >= MIN_JUDGES

    def is_full(self):
        """Check if the tribunal is full (i.e., has 5 judges)."""
        return self.judges.count() == MAX_JUDGES
