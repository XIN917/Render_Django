from django.db import models
from django.conf import settings

class TFM(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='tfms/')
    attachment = models.FileField(upload_to='tfms/attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='submitted_tfms',
        on_delete=models.CASCADE
    )
    directors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='directed_tfms'
    )

    def __str__(self):
        return self.title


class TFMReview(models.Model):
    tfm = models.OneToOneField(TFM, on_delete=models.CASCADE, related_name='review')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviews_done'
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=[('approved', 'Approved'), ('rejected', 'Rejected')])
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Review of {self.tfm.title} by {self.reviewed_by}"
