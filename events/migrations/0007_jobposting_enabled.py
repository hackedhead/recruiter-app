# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-16 21:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20170416_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobposting',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]