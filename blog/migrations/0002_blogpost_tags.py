# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-12 19:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
