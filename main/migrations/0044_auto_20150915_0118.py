# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_auto_20150912_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='drift',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='super_asset_class',
            field=models.CharField(choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('EQUITY_INT', 'EQUITY_INT'), ('EQUITY_UK', 'EQUITY_UK'), ('EQUITY_JAPAN', 'EQUITY_JAPAN'), ('EQUITY_AS', 'EQUITY_AS'), ('EQUITY_CN', 'EQUITY_CN'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT'), ('FIXED_INCOME_UK', 'FIXED_INCOME_UK'), ('FIXED_INCOME_JAPAN', 'FIXED_INCOME_JAPAN'), ('FIXED_INCOME_AS', 'FIXED_INCOME_AS'), ('FIXED_INCOME_CN', 'FIXED_INCOME_CN')], max_length=255),
        ),
    ]
