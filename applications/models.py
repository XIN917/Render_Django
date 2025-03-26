from django.db import models
from django.conf import settings  # Import User model dynamically
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL  # Reference the custom User model

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
    certificate = models.FileField(upload_to='certificates/', null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.certificate and not self.certificate.name.lower().endswith('.pdf'):
            raise ValidationError("Only PDF certificates are allowed.")
        
        super().clean()

    def approve(self):
        """Approve application, upgrade user to teacher."""
        if self.status != self.PENDING:
            raise ValidationError("Cannot approve an application that isn't pending.")
        
        self.status = self.APPROVED
        self.user.role = "teacher"
        self.user.save()
        self.save()

    def reject(self):
        """Reject application without changing the user role."""
        if self.status != self.PENDING:
            raise ValidationError("Cannot reject an application that isn't pending.")
        
        self.status = self.REJECTED
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.status}"