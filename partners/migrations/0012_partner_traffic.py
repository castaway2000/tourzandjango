# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-02 02:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0011_endorsement'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='traffic',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
