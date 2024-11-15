from django.db import models

class Student(models.Model):
    student_id = models.CharField(max_length=15,unique=True)
    name = models.CharField(max_length=30)
    age = models.IntegerField(default=0)

# Create your models here.
