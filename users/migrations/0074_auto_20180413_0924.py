# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-13 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_auto_20180413_0700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generalprofile',
            name='referral_code',
            field=models.CharField(max_length=8, null=True),
        ),
    ]
