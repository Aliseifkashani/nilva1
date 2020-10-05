from __future__ import unicode_literals
from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin , BaseUserManager
# from django.contrib.postgres.fields import ArrayField
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
    time_created = models.DateField(default=now)
    buffer_time = models.DateField(default=now)
    time_to_send = models.DateField(default=now)
    notification_types = models.CharField(
        max_length=100,
        default='email, sms, telegram bot, firebase',
        help_text='separating with \', \''
    )
    repeat = models.IntegerField(default=1)
    interval = models.IntegerField(default=24, help_text='in hour')
    task_id = models.CharField(default='', max_length=100, blank=True)

    def __str__(self):
        return self.title + ' in ' + str(self.time_to_send)


# class UserManager(BaseUserManager):
#
#     def _create_user(self, email, password, **extra_fields):
#         """
#         Creates and saves a User with the given email,and password.
#         """
#         if not email:
#             raise ValueError('The given email must be set')
#         try:
#             with transaction.atomic():
#                 user = self.model(email=email, **extra_fields)
#                 user.set_password(password)
#                 user.save(using=self._db)
#                 return user
#         except:
#             raise
#
#     def create_user(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)
#         return self._create_user(email, password, **extra_fields)
#
#     def create_superuser(self, email, password, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#
#         return self._create_user(email, password=password, **extra_fields)
#
#
# class User(AbstractBaseUser):
#     """
#     An abstract base class implementing a fully featured User model with
#     admin-compliant permissions.
#
#     """
#     username = models.CharField(max_length=100, unique=True, default='')
#     password = models.CharField(max_length=100, default='')
#     email = models.EmailField(max_length=40, unique=True, default='')
#     first_name = models.CharField(max_length=30, blank=True)
#     last_name = models.CharField(max_length=30, blank=True)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     date_joined = models.DateTimeField(default=timezone.now)
#     chat_id = models.CharField(max_length=20, default='')
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['email']
#
#     def save(self, *args, **kwargs):
#         super(User, self).save(*args, **kwargs)
#         return self
