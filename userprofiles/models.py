from django.db import models
from django.contrib.auth.model import User

# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    display_name = models.CharField(max_length=64)
