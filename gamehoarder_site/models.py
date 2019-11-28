# Create your models here.
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, auto_created=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user

