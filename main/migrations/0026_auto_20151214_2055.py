# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20151214_0400'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='etf',
            field=models.BooleanField(help_text='Is this an Exchange Traded Fund (True) or Mutual Fund (False)?', default=True),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=127, help_text='Name of the region')),
                ('description', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.AddField(
            model_name='ticker',
            name='ethical',
            field=models.BooleanField(help_text='Is this an ethical instrument?', default=False),
        ),
        migrations.AddField(
            model_name='ticker',
            name='region',
            field=models.ForeignKey(to='main.Region', null=True),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='investment_type',
            field=models.CharField(max_length=255, choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS')]),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='super_asset_class',
            field=models.CharField(max_length=255, choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('EQUITY_INT', 'EQUITY_INT'), ('EQUITY_UK', 'EQUITY_UK'), ('EQUITY_JAPAN', 'EQUITY_JAPAN'), ('EQUITY_AS', 'EQUITY_AS'), ('EQUITY_CN', 'EQUITY_CN'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT'), ('FIXED_INCOME_UK', 'FIXED_INCOME_UK'), ('FIXED_INCOME_JAPAN', 'FIXED_INCOME_JAPAN'), ('FIXED_INCOME_AS', 'FIXED_INCOME_AS'), ('FIXED_INCOME_CN', 'FIXED_INCOME_CN')]),
        ),
    ]
