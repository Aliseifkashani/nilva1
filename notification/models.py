from __future__ import unicode_literals
from datetime import timedelta
from django.db import models
from django.utils.timezone import now


class Notification(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    creator = models.CharField(max_length=20, default='')
    relevant_staff = models.CharField(max_length=1000, help_text='separating with \', \'', default='')
    notification_types = models.CharField(
        max_length=70,
        default='email, sms, telegram bot, firebase',
        help_text='separating with \', \''
    )
    time_created = models.DateTimeField(default=now)
    time_to_send = models.DateTimeField(default=now)
    repeat = models.IntegerField(default=1)
    interval = models.IntegerField(default=24, help_text='in hour')
    task_id = models.CharField(max_length=80, default='', null=True, blank=True)

    # If settings.USE_TZ was False we didn't need to this timedelta, but it should be True for syncing with celery
    # timezone
    def __str__(self):
        return self.title + ' in ' + str((self.time_to_send + timedelta(minutes=210)).strftime('%Y-%m-%d %H:%M'))
