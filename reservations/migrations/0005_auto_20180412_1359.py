# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-12 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_auto_20180407_2319'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='occasion',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(default='Upcoming reservation', max_length=30),
        ),
    ]
