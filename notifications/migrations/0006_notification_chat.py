# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-31 00:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0011_chatmessage_is_automatic'),
        ('notifications', '0005_auto_20181230_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='chat',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='chats.Chat'),
        ),
    ]
