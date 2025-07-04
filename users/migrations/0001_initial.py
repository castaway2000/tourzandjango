# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-08 11:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GuideProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('interests', models.TextField(blank=True, default=None, null=True)),
                ('bio', models.TextField(blank=True, default=None, null=True)),
                ('date_of_birth', models.DateField(blank=True, default=None, null=True)),
                ('age', models.IntegerField(default=0)),
                ('header_image', models.ImageField(blank=True, default=None, null=True, upload_to='guides/header_image')),
                ('profile_image', models.ImageField(blank=True, default=None, null=True, upload_to='guides/header_image')),
                ('optional_image', models.ImageField(blank=True, default=None, null=True, upload_to='guides/header_image')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.City')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
