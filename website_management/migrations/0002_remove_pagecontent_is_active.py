# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-22 21:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website_management', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagecontent',
            name='is_active',
        ),
    ]
