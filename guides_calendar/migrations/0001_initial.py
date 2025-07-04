# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-24 14:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, default=None, null=True)),
                ('time_from', models.DateTimeField(blank=True, default=None, null=True)),
                ('time_to', models.DateTimeField(blank=True, default=None, null=True)),
                ('is_week_start', models.BooleanField(default=False)),
                ('is_day_start', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Calendar',
                'verbose_name_plural': 'Calendars',
            },
        ),
    ]
