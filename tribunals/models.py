from django.db import models
from tfms.models import TFM
from slots.models import Slot
from users.models import User
from judges.models import Judge

class Tribunal(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE, unique=True)  
    # Reverse relationship: You can access the Tribunal from a TFM instance using `tfm.tribunal`
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='tribunals')
    index = models.IntegerField(default=1)

    class Meta:
        unique_together = (('slot', 'index'),)

    def __str__(self):
        return f"Tribunal for {self.tfm.title}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Only auto-assign if the index was not explicitly passed
            if self.index == 1 and self.slot.tribunals.filter(index=1).exists():
                existing_indexes = set(self.slot.tribunals.values_list('index', flat=True))
                next_index = 1  # start from 1
                while next_index in existing_indexes:
                    next_index += 1

                if next_index > self.slot.max_tfms:
                    raise ValueError(f"Slot '{self.slot}' has reached its maximum number of TFMs.")

                self.index = next_index

        super().save(*args, **kwargs)

    def add_judge(self, user: User, role: str):
        """Helper method to add a judge with a role."""
        return Judge.objects.create(tribunal=self, user=user, role=role)
    
    def get_semester(self):
        return self.slot.track.semester

    def is_ready(self):
        """Check if the tribunal is ready (has enough judges)."""
        return self.judges.count() >= self.get_semester().min_judges

    def is_full(self):
        """Check if the tribunal is full."""
        return self.judges.count() >= self.get_semester().max_judges
