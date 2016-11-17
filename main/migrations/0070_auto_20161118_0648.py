# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0069_auto_20161117_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttype',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA'), (9, 'SEP IRA'), (10, '403K Account'), (11, 'SIMPLE IRA Account (Savings Incentive Match Plans for Employees)'), (12, 'SARSEP Account (Salary Reduction Simplified Employee Pension)'), (13, 'Payroll Deduction IRA Account'), (14, 'Profit-Sharing Account'), (15, 'Defined Benefit Account'), (16, 'Money Purchase Account'), (17, 'Employee Stock Ownership Account (ESOP)'), (18, 'Governmental Account'), (19, '457 Account'), (20, '409A Nonqualified Deferred Compensation Account'), (21, '403B Account')]),
        ),
        migrations.AlterField(
            model_name='activitylogevent',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, choices=[(0, 'PLACE_MARKET_ORDER'), (1, 'CANCEL_MARKET_ORDER'), (2, 'ARCHIVE_GOAL_REQUESTED'), (3, 'ARCHIVE_GOAL'), (4, 'REACTIVATE_GOAL'), (5, 'APPROVE_SELECTED_SETTINGS'), (6, 'REVERT_SELECTED_SETTINGS'), (7, 'SET_SELECTED_SETTINGS'), (8, 'UPDATE_SELECTED_SETTINGS'), (9, 'GOAL_WITHDRAWAL'), (10, 'GOAL_DEPOSIT'), (11, 'GOAL_BALANCE_CALCULATED'), (12, 'GOAL_WITHDRAWAL_EXECUTED'), (13, 'GOAL_DEPOSIT_EXECUTED'), (14, 'GOAL_DIVIDEND_DISTRIBUTION'), (15, 'GOAL_FEE_LEVIED'), (16, 'GOAL_REBALANCE_EXECUTED'), (17, 'GOAL_TRANSFER_EXECUTED'), (18, 'GOAL_ORDER_DISTRIBUTION'), (19, 'RETIRESMARTZ_PROTECTIVE_MOVE'), (20, 'RETIRESMARTZ_DYNAMIC_MOVE'), (21, 'RETIRESMARTZ_SPENDABLE_INCOME_UP_CONTRIB_DOWN'), (22, 'RETIRESMARTZ_SPENDABLE_INCOME_DOWN_CONTRIB_UP'), (23, 'RETIRESMARTZ_RETIREMENT_AGE_ADJUSTED'), (24, 'RETIRESMARTZ_IS_A_SMOKER'), (25, 'RETIRESMARTZ_IS_NOT_A_SMOKER'), (26, 'RETIRESMARTZ_EXERCISE_ONLY'), (27, 'RETIRESMARTZ_WEIGHT_AND_HEIGHT_ONLY'), (28, 'RETIRESMARTZ_COMBINATION_WELLBEING_ENTRIES'), (29, 'RETIRESMARTZ_ALL_WELLBEING_ENTRIES'), (30, 'RETIRESMARTZ_ON_TRACK_NOW'), (31, 'RETIRESMARTZ_OFF_TRACK_NOW'), (32, 'RETIRESMARTZ_CONTRIB_UP_SPENDING_DOWN')]),
        ),
    ]
