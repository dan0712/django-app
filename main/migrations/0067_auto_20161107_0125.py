# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0066_auto_20161104_0253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylogevent',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True, choices=[(0, 'PLACE_MARKET_ORDER'), (1, 'CANCEL_MARKET_ORDER'), (2, 'ARCHIVE_GOAL_REQUESTED'), (3, 'ARCHIVE_GOAL'), (4, 'REACTIVATE_GOAL'), (5, 'APPROVE_SELECTED_SETTINGS'), (6, 'REVERT_SELECTED_SETTINGS'), (7, 'SET_SELECTED_SETTINGS'), (8, 'UPDATE_SELECTED_SETTINGS'), (9, 'GOAL_WITHDRAWAL'), (10, 'GOAL_DEPOSIT'), (11, 'GOAL_BALANCE_CALCULATED'), (12, 'GOAL_WITHDRAWAL_EXECUTED'), (13, 'GOAL_DEPOSIT_EXECUTED'), (14, 'GOAL_DIVIDEND_DISTRIBUTION'), (15, 'GOAL_FEE_LEVIED'), (16, 'GOAL_REBALANCE_EXECUTED'), (17, 'GOAL_TRANSFER_EXECUTED'), (18, 'GOAL_ORDER_DISTRIBUTION'), (19, 'RETIRESMARTZ_PROTECTIVE_MOVE')]),
        ),
    ]
