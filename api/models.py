from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = 'MANAGER', ('Manager')
        USER = 'USER', ('User')

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USER)


class Tasks(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    links = models.TextField()
    progress = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return self.title
