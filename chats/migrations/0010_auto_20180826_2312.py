# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-26 20:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0009_chat_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='order',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.Order'),
        ),
    ]
