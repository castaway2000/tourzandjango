# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-24 22:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0051_remove_generalprofile_phone_is_validated'),
    ]

    operations = [
        migrations.RenameField(
            model_name='generalprofile',
            old_name='is_trusted',
            new_name='phone_is_validated',
        ),
        migrations.RemoveField(
            model_name='generalprofile',
            name='is_verified',
        ),
    ]
