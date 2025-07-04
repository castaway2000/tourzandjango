# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-13 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import tourzan.storage_backends
import utils.uploadings


class Migration(migrations.Migration):

    dependencies = [
        ('user_verification', '0004_auto_20180413_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentscan',
            name='file',
            field=models.FileField(blank=True, default=None, null=True, storage=tourzan.storage_backends.PrivateMediaStorageSameLocation(), upload_to=utils.uploadings.upload_path_handler_user_scanned_docs),
        ),
    ]
