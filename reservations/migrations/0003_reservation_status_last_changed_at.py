# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-08 02:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_reservation_hotelname'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='status_last_changed_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
