# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_goal_satellite_pct'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='satelliteAlloc',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='security_question_2',
            field=models.CharField(default='', max_length=255, choices=[('What was your first car?', 'What was your first car?'), ('What was your favourite subject at school?', 'What was your favourite subject at school?'), ('In what month was your father born?', 'In what month was your father born?')]),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='investment_type',
            field=models.CharField(max_length=255, choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS'), ('MANAGED_FUNDS', 'MANAGED_FUNDS')]),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='super_asset_class',
            field=models.CharField(max_length=255, choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('EQUITY_INT', 'EQUITY_INT'), ('EQUITY_UK', 'EQUITY_UK'), ('EQUITY_JAPAN', 'EQUITY_JAPAN'), ('EQUITY_AS', 'EQUITY_AS'), ('EQUITY_CN', 'EQUITY_CN'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT'), ('FIXED_INCOME_UK', 'FIXED_INCOME_UK'), ('FIXED_INCOME_JAPAN', 'FIXED_INCOME_JAPAN'), ('FIXED_INCOME_AS', 'FIXED_INCOME_AS'), ('FIXED_INCOME_CN', 'FIXED_INCOME_CN'), ('MANAGED_FUNDS_AU', 'MANAGED_FUNDS_AU')]),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_question_2',
            field=models.CharField(default='', max_length=255, choices=[('What was your first car?', 'What was your first car?'), ('What was your favourite subject at school?', 'What was your favourite subject at school?'), ('In what month was your father born?', 'In what month was your father born?')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_question_2',
            field=models.CharField(default='', max_length=255, choices=[('What was your first car?', 'What was your first car?'), ('What was your favourite subject at school?', 'What was your favourite subject at school?'), ('In what month was your father born?', 'In what month was your father born?')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='middle_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='middle name(s)'),
        ),
    ]
