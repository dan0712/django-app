# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20151001_1221'),
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketCap',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('value', models.FloatField(default=0)),
                ('ticker', models.ForeignKey(related_name='market_cap', to='main.Ticker')),
            ],
        ),
    ]
