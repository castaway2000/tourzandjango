# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-22 23:45
from __future__ import unicode_literals

from django.db import migrations, models
import utils.general


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0060_tour_image_large'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='slug',
            field=models.SlugField(blank=True, default=utils.general.random_string_creating, max_length=200, null=True),
        ),
    ]
