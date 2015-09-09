# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0003_portfolioset_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioByRisk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('risk', models.FloatField()),
                ('expectedReturn', models.FloatField()),
                ('volatility', models.FloatField()),
                ('allocations', models.TextField(default='{}')),
                ('portfolio_set', models.ForeignKey(to='portfolios.PortfolioSet')),
            ],
        ),
    ]
