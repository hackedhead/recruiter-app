# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-16 15:06
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_remove_candidate_applying_for'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='application',
            options={'ordering': ['-event'], 'verbose_name': 'Candidate Job Associations'},
        ),
        migrations.AlterModelOptions(
            name='candidate',
            options={'verbose_name_plural': 'Candidates'},
        ),
        migrations.AlterField(
            model_name='candidate',
            name='phone',
            field=models.CharField(blank=True, max_length=16, null=True, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format: +999999999. Up to 15 digits allowed.', regex='^\\+?1?\\d{8,15}$')]),
        ),
    ]