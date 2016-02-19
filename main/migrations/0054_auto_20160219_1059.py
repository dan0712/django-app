# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from main.models import Advisor, ClientAccount


def populate_ps(apps, schema_editor):
    for a in Advisor.objects.all():
        if not hasattr(a, 'default_portfolio_set'):
            a.default_portfolio_set = a.firm.default_portfolio_set
            a.save()
    for a in ClientAccount.objects.all():
        if not hasattr(a, 'default_portfolio_set'):
            a.default_portfolio_set = a.primary_owner.advisor.default_portfolio_set
            a.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_auto_20160219_1045'),
    ]

    operations = [
        migrations.RunPython(populate_ps),
        migrations.RenameField(
            model_name='transaction',
            old_name='type_int',
            new_name='type'
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.IntegerField(choices=[(0, 'ALLOCATION'), (1, 'DEPOSIT'), (2, 'WITHDRAWAL'), (3, 'REBALANCE'), (4, 'MARKET_CHANGE'), (5, 'FEE')]),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='default_portfolio_set',
            field=models.ForeignKey(to='main.PortfolioSet'),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='account_type',
            field=models.IntegerField(choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account')]),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='default_portfolio_set',
            field=models.ForeignKey(to='main.PortfolioSet'),
        ),
        migrations.AlterField(
            model_name='firm',
            name='default_portfolio_set',
            field=models.ForeignKey(to='main.PortfolioSet'),
        ),
    ]
