from django.contrib.auth.models import AbstractUser  #user객체 상속
from django.db import models

class CustomUser(AbstractUser):
    school_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    range = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username