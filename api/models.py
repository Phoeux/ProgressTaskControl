from django.contrib.auth import password_validation
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = 'MANAGER', ('Manager')
        USER = 'USER', ('User')

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USER)

    def save(self, *args, **kwargs):
        if self.password is not None:
            password_validation.password_changed(self.password, self)
            if not self.is_superuser:
                self.set_password(self.password)
            super().save(*args, **kwargs)


class Tasks(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    links = models.ManyToManyField('Links')
    progress = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='simple_user')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='manager_user')
    finished = models.BooleanField(default=False)
    date_to_check = models.DateField(null=True, blank=True)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'


class Links(models.Model):
    url = models.URLField()
    complited = models.BooleanField(default=False)


# class LinksTasks(models.Model):
#     links = models.ForeignKey(Links, on_delete=models.DO_NOTHING, related_name='linkstasks_links')
#     tasks = models.ForeignKey(Tasks, on_delete=models.DO_NOTHING, related_name='linkstasks_tasks')