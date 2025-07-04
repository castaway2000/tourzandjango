# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-02-18 03:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0028_auto_20190503_0254'),
        ('tours', '0067_tour_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuratedTours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('age', models.IntegerField(blank=True, default=None, null=True)),
                ('gender', models.CharField(blank=True, default=None, max_length=80, null=True)),
                ('origin', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('interests', models.CharField(blank=True, default=None, max_length=500, null=True)),
                ('language', models.CharField(blank=True, default=None, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('destination', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='locations.City')),
            ],
        ),
    ]
