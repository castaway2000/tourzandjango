# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-01-07 15:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0037_auto_20180107_1740'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GuideAnswers',
            new_name='GuideAnswer',
        ),
    ]
