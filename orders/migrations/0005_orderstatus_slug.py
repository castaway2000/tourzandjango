# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-19 20:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20170319_1957'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderstatus',
            name='slug',
            field=models.SlugField(blank=True, default=None, null=True, unique=True),
        ),
    ]
