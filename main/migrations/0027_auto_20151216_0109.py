# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20151214_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetclass',
            name='investment_type',
            field=models.CharField(max_length=255, choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS'), ('MIXED', 'MIXED')]),
        ),
    ]
