# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-11 16:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0038_auto_20180611_1900'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TourActivityDescription',
            new_name='TourActivityItem',
        ),
    ]
