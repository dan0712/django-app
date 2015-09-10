# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_ticker_currency'),
        ('portfolios', '0005_auto_20150909_2207'),
    ]

    operations = [
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('q', models.FloatField()),
                ('assets', models.ManyToManyField(to='main.AssetClass')),
                ('portfolio_set', models.ForeignKey(to='portfolios.PortfolioSet')),
            ],
        ),
    ]
