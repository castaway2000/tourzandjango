# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-08 19:19
from __future__ import unicode_literals

from django.db import migrations, models
import utils.general


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0011_auto_20180208_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='slug',
            field=models.SlugField(blank=True, default=utils.general.random_string_creating, null=True),
        ),
    ]
