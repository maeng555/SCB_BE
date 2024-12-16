from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class Profile(models.Model):
    school_id = models.IntegerField(unique=True)
    range = models.CharField(max_length=20)
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    def __str__(self):
        return self.name
        

