from django.conf import settings
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

from common.constants import UserRole


class Account(AbstractUser):


    role = models.CharField(max_length=20, choices=[(role.value, role.name) for role in UserRole])

    class Meta:
        swappable = settings.AUTH_USER_MODEL


        indexes = [
            models.Index(fields=['email']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email'),  # Add unique constraint to the email field
        ]
    # Other fields and methods...


