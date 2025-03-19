from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """Custom manager to handle user creation without a username field."""

    def create_user(self, email, full_name, password=None, **extra_fields):
        """Create a user with a default password if none is provided."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        
        # Set default password if none is provided
        if not password:
            password = "12345678"

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """Creates a superuser with staff and superuser permissions."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'teacher')

        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractUser):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField(unique=True)  # Use email as the primary identifier
    full_name = models.CharField(max_length=100)  # Single field for full name
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)

    USERNAME_FIELD = 'email'  # Set email as the unique identifier
    REQUIRED_FIELDS = ['full_name']  # Fields required when using createsuperuser

    objects = UserManager()  # Assign the custom UserManager

    def __str__(self):
        return self.email
