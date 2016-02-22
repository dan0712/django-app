# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_transaction_satellitealloc'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='from_account',
            new_name='from_goal',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='to_account',
            new_name='to_goal',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='account',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='type',
            new_name='reason'
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='cash_balance',
            field=models.FloatField(help_text='The amount of cash in this account available to be used.', default=0),
        ),
        migrations.AddField(
            model_name='goal',
            name='cash_balance',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='reason',
            field=models.IntegerField(choices=[(0, 'DIVIDEND'), (1, 'DEPOSIT'), (2, 'WITHDRAWAL'), (3, 'REBALANCE'), (4, 'TRANSFER'), (5, 'FEE')], db_index=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
