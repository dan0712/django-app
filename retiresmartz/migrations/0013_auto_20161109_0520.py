# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0012_auto_20161107_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='atc',
            field=models.PositiveIntegerField(help_text='Annual personal after-tax contributions', blank=True),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='btc',
            field=models.PositiveIntegerField(help_text='Annual personal before-tax contributions', blank=True),
        ),
    ]
