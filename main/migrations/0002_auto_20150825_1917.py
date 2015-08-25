# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticker',
            name='asset_classes',
        ),
        migrations.AddField(
            model_name='ticker',
            name='asset_classes',
            field=models.ForeignKey(blank=True, related_name='tickers', default=0, to='main.AssetClass'),
            preserve_default=False,
        ),
    ]
