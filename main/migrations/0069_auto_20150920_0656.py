# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0068_auto_20150920_0600'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialPlanAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('annual_contribution_cents', models.CharField(max_length=100, null=True)),
                ('account', models.ForeignKey(to='main.ClientAccount')),
            ],
        ),
        migrations.CreateModel(
            name='FinancialPlanExternalAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('account_type', models.CharField(max_length=100)),
                ('balance_cents', models.FloatField(default=0, null=True)),
                ('annual_contribution_cents', models.FloatField(default=0, null=True)),
                ('account_owner', models.CharField(max_length=100, null=True)),
                ('institution_name', models.CharField(max_length=255, null=True)),
                ('investment_type', models.CharField(max_length=100, null=True)),
                ('advisor_fee_percent', models.CharField(max_length=100, null=True)),
                ('account', models.ForeignKey(to='main.ClientAccount')),
            ],
        ),
        migrations.RemoveField(
            model_name='financialplan',
            name='accounts',
        ),
    ]
