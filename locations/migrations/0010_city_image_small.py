# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-08 19:04
from __future__ import unicode_literals

from django.db import migrations, models
import utils.uploadings


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0009_auto_20171012_0527'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='image_small',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=utils.uploadings.upload_path_handler_city),
        ),
    ]
