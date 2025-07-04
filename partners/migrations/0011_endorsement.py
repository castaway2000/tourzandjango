# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-31 06:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0010_integrationpartners'),
    ]

    operations = [
        migrations.CreateModel(
            name='Endorsement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(null=True)),
                ('url', models.URLField(null=True)),
                ('logo', models.ImageField(null=True, upload_to='')),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
    ]
