# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-23 23:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0016_remove_guideprofile_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='guideprofile',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
