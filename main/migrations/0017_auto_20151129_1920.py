# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('portfolios', '0004_auto_20151129_0531'),
        ('main', '0016_goal_custom_portfolio_set'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='asia_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='asia_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='asia_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='au_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='au_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='au_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='china_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='china_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='china_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='dm_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='dm_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='dm_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='em_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='em_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='em_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='europe_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='europe_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='europe_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='japan_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='japan_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='japan_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='uk_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='uk_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='uk_size',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='usa_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='usa_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='usa_size',
        ),
        migrations.AddField(
            model_name='goal',
            name='custom_regions',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='performer',
            name='portfolio_set',
            field=models.ForeignKey(to='portfolios.PortfolioSet', default=1),
            preserve_default=False,
        ),
    ]
