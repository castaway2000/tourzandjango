# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-11 16:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0040_auto_20180611_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='tourprogramitem',
            name='duration',
            field=models.IntegerField(default=0),
        ),
    ]
