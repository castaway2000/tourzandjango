# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-18 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0037_auto_20180617_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='uuid',
            field=models.CharField(blank=True, default=None, max_length=48, null=True),
        ),
    ]
