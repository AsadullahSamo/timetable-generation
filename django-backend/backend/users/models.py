from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='TEACHER')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"