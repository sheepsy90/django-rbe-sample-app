from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User)
    uid = models.IntegerField()
    password = models.CharField(max_length=128)