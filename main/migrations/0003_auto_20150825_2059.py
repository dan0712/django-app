# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150825_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticker',
            name='asset_classes',
        ),
        migrations.RemoveField(
            model_name='ticker',
            name='primary',
        ),
        migrations.AddField(
            model_name='ticker',
            name='asset_class',
            field=models.ForeignKey(related_name='tickers', to='main.AssetClass', default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ticker',
            name='description',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='display_name',
            field=models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid display name, only allowed this characters (a-zA-Z0-9_)', regex='^[a-zA-Z0-9_]+$')], max_length=255),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='ordering',
            field=models.IntegerField(editable=False, default=0),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='symbol',
            field=models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid symbol format', regex='[^ ]')], max_length=10),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='unit_price',
            field=models.FloatField(editable=False),
        ),
    ]
