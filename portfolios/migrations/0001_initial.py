# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyAssetClass',
            fields=[
            ],
            options={
                'verbose_name': 'Asset class',
                'verbose_name_plural': 'Asset classes',
                'proxy': True,
            },
            bases=('main.assetclass',),
        ),
        migrations.CreateModel(
            name='ProxyTicker',
            fields=[
            ],
            options={
                'verbose_name': 'Tickers',
                'verbose_name_plural': 'Ticker',
                'proxy': True,
            },
            bases=('main.ticker',),
        ),
    ]
