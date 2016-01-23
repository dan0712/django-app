# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_auto_20160123_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('REBALANCE', 'REBALANCE'), ('ALLOCATION', 'ALLOCATION'), ('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL'), ('MARKET_CHANGE', 'MARKET_CHANGE')], max_length=255),
        ),
    ]
