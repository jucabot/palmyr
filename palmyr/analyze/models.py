from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class FileDataSource(models.Model):
    name = models.CharField(max_length=100)
    path = models.FileField(upload_to='user_data')
    user = models.ForeignKey(User)
    
    