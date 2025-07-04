# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-04 19:37
from __future__ import unicode_literals

from django.db import migrations, models
import utils.uploadings


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0018_guideprofile_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='guideprofile',
            name='webcam_image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=utils.uploadings.upload_path_handler_guide_webcam_image),
        ),
    ]
