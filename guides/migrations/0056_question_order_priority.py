# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-13 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0055_auto_20180804_0202'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='order_priority',
            field=models.IntegerField(default=0),
        ),
    ]
