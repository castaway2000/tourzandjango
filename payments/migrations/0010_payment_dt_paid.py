# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-25 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0009_remove_payment_date_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='dt_paid',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
