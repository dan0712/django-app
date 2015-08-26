# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyAssetClass',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Asset classes',
                'proxy': True,
                'verbose_name': 'Asset class',
            },
            bases=('main.assetclass',),
        ),
        migrations.CreateModel(
            name='ProxyTicker',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Ticker',
                'proxy': True,
                'verbose_name': 'Tickers',
            },
            bases=('main.ticker',),
        ),
    ]
