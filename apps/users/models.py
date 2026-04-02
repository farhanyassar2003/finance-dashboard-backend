from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ("viewer", "Viewer"),
        ("analyst", "Analyst"),
        ("admin", "Admin"),
    )
    
    DEPARTMENT_CHOICES = (
        ("finance", "Finance"),
        ("operations", "Operations"),
        ("marketing", "Marketing"),
        ("hr", "HR"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="viewer",
    )

    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.username} - {self.role}"
