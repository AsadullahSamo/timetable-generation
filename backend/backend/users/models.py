from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    # role = models.CharField(max_length=10, choices=ROLES, default='TEACHER')
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)