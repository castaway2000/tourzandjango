# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-07-21 18:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_auto_20170721_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentscan',
            name='status',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.ScanStatus'),
        ),
    ]
