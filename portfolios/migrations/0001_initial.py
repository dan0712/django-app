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
                'proxy': True,
                'verbose_name': 'Asset class',
                'verbose_name_plural': 'Asset classes',
            },
            bases=('main.assetclass',),
        ),
        migrations.CreateModel(
            name='ProxyTicker',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Tickers',
                'verbose_name_plural': 'Ticker',
            },
            bases=('main.ticker',),
        ),
    ]
