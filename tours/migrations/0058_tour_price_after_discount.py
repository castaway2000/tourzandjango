# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-19 23:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0057_auto_20180717_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='price_after_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
