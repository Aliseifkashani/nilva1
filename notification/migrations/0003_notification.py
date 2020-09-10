# Generated by Django 3.1.1 on 2020-09-10 12:46

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_auto_20200910_0729'),
    ]

    operations = [
        migrations.CreateModel(
            name='notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('relevant_staff', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=10), size=None)),
                ('time_created', models.DateField(default=datetime.datetime(2020, 9, 10, 12, 46, 59, 482382))),
                ('time_to_send', models.DateField()),
            ],
        ),
    ]
