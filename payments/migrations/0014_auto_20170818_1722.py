# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-18 14:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0013_auto_20170818_1516'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentmethod',
            old_name='card_type',
            new_name='type',
        ),
    ]
