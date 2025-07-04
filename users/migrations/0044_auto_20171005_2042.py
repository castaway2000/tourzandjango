# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-05 17:42
from __future__ import unicode_literals

from django.db import migrations, models
import utils.uploadings


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_auto_20171005_0317'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalprofile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='generalprofile',
            name='webcam_image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=utils.uploadings.upload_path_handler_guide_webcam_image),
        ),
    ]
