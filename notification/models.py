from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.timezone import now


class Notification(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()
    creator = models.CharField(max_length=100, default='')
    relevant_staff = models.CharField(
        max_length=200,
        help_text='separating with \', \'',
        default=''
    )
    time_created = now
    due_date = models.DateTimeField(default=now)
    time_to_send = models.DateTimeField(default=now)
    notification_types = models.CharField(
        max_length=100,
        default='email, sms, telegram bot, firebase',
        help_text='separating with \', \''
    )
    repeat = models.IntegerField(default=1)
    interval = models.IntegerField(default=24, help_text='in hour')
    task_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title + ' in ' + str(self.time_to_send)
