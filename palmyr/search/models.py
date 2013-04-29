from django.db import models
from django.contrib.auth.models import User


# Create your models here.

    
class Domain(models.Model):
    name = models.CharField(max_length=500)
    key = models.CharField(max_length=500)
    description = models.TextField()
    icon_path = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    
class Workspace(models.Model):
    name = models.CharField(max_length=500)
    value = models.TextField()
    user = models.ForeignKey(User)
    icon_path = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name