# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2019-04-15 17:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_auto_20190408_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date_time',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Event date'),
        ),
    ]
