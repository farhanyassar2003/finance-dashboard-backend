from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager as DjangoUserManager

class CustomUserManager(DjangoUserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")

        return super().create_superuser(username, email, password, **extra_fields)

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
    
    objects = CustomUserManager() 

    
    def __str__(self):
        return f"{self.username} - {self.role}"
