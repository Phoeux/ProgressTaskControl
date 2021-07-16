from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tasks(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    links = models.TextField()
    progress = models.CharField(max_length=20)

    def __str__(self):
        return self.title
