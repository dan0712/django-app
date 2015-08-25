# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150825_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetclass',
            name='asset_class_explanation',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='display_order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='donut_order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='name',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(message='Invalid asset name, only allowed this characters (a-zA-Z0-9_)', regex='^[a-zA-Z0-9_]+$')]),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='tickers_explanation',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='display_name',
            field=models.CharField(max_length=255),
        ),
    ]
