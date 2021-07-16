from django.db import models


class Tasks(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    links = models.TextField()
    progress = models.CharField(max_length=20)

    def __str__(self):
        return self.title
