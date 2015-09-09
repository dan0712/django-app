# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20150905_0950'),
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioSet',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('risk_free_rate', models.FloatField()),
                ('tau', models.FloatField()),
                ('asset_classes', models.ManyToManyField(to='main.AssetClass', related_name='portfolio_sets')),
            ],
        ),
    ]
