# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-27 01:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0047_generalprofile_is_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='generalprofile',
            name='webcam_image',
        ),
    ]
