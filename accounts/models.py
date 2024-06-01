from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from .models import *

class fosUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True, blank=False)
    is_approved = models.BooleanField(default=False)
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name or f"Profile of {self.user.username}"

