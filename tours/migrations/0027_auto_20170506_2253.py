# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-06 19:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0026_auto_20170506_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='order',
        ),
        migrations.RemoveField(
            model_name='review',
            name='user',
        ),
        migrations.DeleteModel(
            name='Review',
        ),
    ]
