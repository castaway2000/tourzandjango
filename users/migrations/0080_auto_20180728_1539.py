# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-28 12:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0079_auto_20180503_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalprofile',
            name='referral_code',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
