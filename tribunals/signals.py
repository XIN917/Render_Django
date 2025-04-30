from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tribunal
from datetime import datetime, date

def recalculate_slot_end_time(slot):
    tribunals = slot.tribunals.all()
    if not tribunals.exists():
        slot.end_time = slot.start_time
    else:
        max_index = tribunals.aggregate(models.Max('index'))['index__max']
        if max_index is None:
            slot.end_time = slot.start_time
        else:
            # Each index represents one TFM slot, starting at 0
            total_duration = (max_index + 1) * slot.tfm_duration
            slot.end_time = (
                datetime.combine(date.today(), slot.start_time) + total_duration
            ).time()
    slot.save(update_fields=["end_time"])

@receiver(post_save, sender=Tribunal)
def update_slot_end_time_on_create_or_update(sender, instance, **kwargs):
    recalculate_slot_end_time(instance.slot)

@receiver(post_delete, sender=Tribunal)
def update_slot_end_time_on_delete(sender, instance, **kwargs):
    recalculate_slot_end_time(instance.slot)
