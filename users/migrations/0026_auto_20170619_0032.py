# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-18 21:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_paymentmethod_is_default'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentcustomer',
            name='user',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='user',
        ),
        migrations.DeleteModel(
            name='PaymentCustomer',
        ),
        migrations.DeleteModel(
            name='PaymentMethod',
        ),
    ]
