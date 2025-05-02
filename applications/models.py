from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from institutions.models import Institution

User = settings.AUTH_USER_MODEL

class TeacherApplication(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="applications", null=True, blank=True)
    attachment = models.FileField(upload_to='attachments/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.attachment and not self.attachment.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF attachments are allowed.")
        super().clean()

    def approve(self):
        if self.status != self.PENDING:
            raise ValidationError("Cannot approve an application that isn't pending.")

        self.status = self.APPROVED
        self.user.role = "teacher"
        self.user.save()

        # 🔗 Link the institution to the user's profile
        profile, _ = self.user.profile.__class__.objects.get_or_create(user=self.user)
        profile.institution = self.institution
        profile.save()

        self.save()

    def reject(self):
        if self.status != self.PENDING:
            raise ValidationError("Cannot reject an application that isn't pending.")
        self.status = self.REJECTED
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.status}"
