# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150825_1917'),
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyTicker',
            fields=[
            ],
            options={
                'verbose_name_plural': 'Ticker',
                'verbose_name': 'Tickers',
                'proxy': True,
            },
            bases=('main.ticker',),
        ),
    ]
