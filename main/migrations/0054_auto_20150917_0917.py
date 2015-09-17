# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_auto_20150917_0442'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='inversion',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='net_change',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='new_balance',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='return_fraction',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(max_length=20, choices=[('REBALANCE', 'REBALANCE'), ('ALLOCATION', 'ALLOCATION'), ('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL'), ('MARKET_CHANGE', 'MARKET_CHANGE')]),
        ),
    ]
