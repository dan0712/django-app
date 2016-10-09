# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0015_auto_20160930_0010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttyperiskprofilegroup',
            name='account_type',
            field=models.IntegerField(unique=True, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA')]),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='account_type',
            field=models.IntegerField(choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA')]),
        ),
    ]
