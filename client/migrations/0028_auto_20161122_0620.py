# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0027_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='APEXAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('apex_account', models.CharField(max_length=32)),
            ],
        ),
        migrations.AlterField(
            model_name='accounttyperiskprofilegroup',
            name='account_type',
            field=models.IntegerField(choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA'), (9, 'SEP IRA'), (10, '403K Account'), (11, 'SIMPLE IRA Account (Savings Incentive Match Plans for Employees)'), (12, 'SARSEP Account (Salary Reduction Simplified Employee Pension)'), (13, 'Payroll Deduction IRA Account'), (14, 'Profit-Sharing Account'), (15, 'Defined Benefit Account'), (16, 'Money Purchase Account'), (17, 'Employee Stock Ownership Account (ESOP)'), (18, 'Governmental Account'), (19, '457 Account'), (20, '409A Nonqualified Deferred Compensation Account'), (21, '403B Account'), (99, 'Other Account')], unique=True),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='account_type',
            field=models.IntegerField(choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA'), (9, 'SEP IRA'), (10, '403K Account'), (11, 'SIMPLE IRA Account (Savings Incentive Match Plans for Employees)'), (12, 'SARSEP Account (Salary Reduction Simplified Employee Pension)'), (13, 'Payroll Deduction IRA Account'), (14, 'Profit-Sharing Account'), (15, 'Defined Benefit Account'), (16, 'Money Purchase Account'), (17, 'Employee Stock Ownership Account (ESOP)'), (18, 'Governmental Account'), (19, '457 Account'), (20, '409A Nonqualified Deferred Compensation Account'), (21, '403B Account'), (99, 'Other Account')]),
        ),
        migrations.AddField(
            model_name='apexaccount',
            name='bs_account',
            field=models.OneToOneField(related_name='apex_account', to='client.ClientAccount'),
        ),
    ]
