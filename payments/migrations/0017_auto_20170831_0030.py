# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-30 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0016_auto_20170830_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='card_number',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
