# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioByRisk',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('risk', models.FloatField()),
                ('expected_return', models.FloatField()),
                ('volatility', models.FloatField()),
                ('allocations', models.TextField(default='{}')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioSet',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('risk_free_rate', models.FloatField()),
                ('tau', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('q', models.FloatField()),
                ('assets', models.TextField()),
                ('portfolio_set', models.ForeignKey(related_name='views', to='portfolios.PortfolioSet')),
            ],
        ),
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
        migrations.AddField(
            model_name='portfolioset',
            name='asset_classes',
            field=models.ManyToManyField(related_name='portfolio_sets', to='main.AssetClass'),
        ),
        migrations.AddField(
            model_name='portfoliobyrisk',
            name='portfolio_set',
            field=models.ForeignKey(related_name='risk_profiles', to='portfolios.PortfolioSet'),
        ),
    ]
