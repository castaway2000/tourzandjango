# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-28 01:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('guides', '0055_auto_20180804_0202'),
        ('orders', '0043_orderstatuschangehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherReviews',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tourist_name', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('tourist_feedback_name', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('tourist_feedback_text', models.TextField(blank=True, default=None, null=True)),
                ('tourist_rating', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('is_tourist_feedback', models.BooleanField(default=False)),
                ('tourist_review_created', models.DateTimeField(blank=True, default=None, null=True)),
                ('tourist_review_updated', models.DateTimeField(blank=True, default=None, null=True)),
                ('guide', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='guides.GuideProfile')),
            ],
        ),
    ]
