from django.contrib import admin
from django import forms

from .models import Notification


class NotificationCreationForm(forms.ModelForm):

    class Meta:
        model = Notification
        exclude = ('task_id', 'time_created')


class NotificationChangeForm(forms.ModelForm):

    class Meta:
        model = Notification
        exclude = ('task_id',)


class NotificationAdmin(admin.ModelAdmin):
    form = NotificationChangeForm
    add_form = NotificationCreationForm
    search_fields = ('title',)
    ordering = ('time_to_send',)
    filter_horizontal = ()


admin.site.register(Notification, NotificationAdmin)
