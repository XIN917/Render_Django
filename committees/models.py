from django.db import models
from users.models import User

class Committee(models.Model):
    ROLE_CHOICES = [
        ('president', 'President'),
        ('secretary', 'Secretary'),
        ('vocal', 'Vocal'),
    ]

    tribunal = models.ForeignKey('tribunals.Tribunal', on_delete=models.CASCADE, related_name='committees')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='committee_roles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = (('tribunal', 'user'),)

    def __str__(self):
        return f"{self.user.get_full_name()} as {self.get_role_display()} in {self.tribunal}"
