from django.db import models
from settings import MEDIA_ROOT

# Create your models here.

class FileDataSource(models.Model):
    name = models.CharField(max_length=100)
    path = models.CharField(max_length=500)