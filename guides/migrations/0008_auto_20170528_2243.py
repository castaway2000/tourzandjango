# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-28 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0007_guideservice_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='guideprofile',
            name='orders_completed_nmb',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='guideprofile',
            name='orders_nmb',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='guideprofile',
            name='orders_reviewed_nmb',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='guideprofile',
            name='orders_with_review_nmb',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='guideprofile',
            name='orders_with_review_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
