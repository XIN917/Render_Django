# tribunals/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Tribunal

@receiver(post_delete, sender=Tribunal)
def update_slot_end_time_on_delete(sender, instance, **kwargs):
    slot = instance.slot
    tfm_count = slot.tribunals.count()
    if tfm_count == 0:
        slot.end_time = slot.start_time
    else:
        from datetime import datetime, date
        total_duration = tfm_count * slot.tfm_duration
        slot.end_time = (
            datetime.combine(date.today(), slot.start_time) + total_duration
        ).time()
    slot.save(update_fields=["end_time"])
