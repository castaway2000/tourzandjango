# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-09 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0006_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='tours/images'),
        ),
    ]
