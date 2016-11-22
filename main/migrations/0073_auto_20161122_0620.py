# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0072_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApexFill',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('price', models.FloatField(help_text='Price for the fill.')),
                ('executed', models.DateTimeField(help_text='The time the trade was executed.')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionApexFill',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('apex_fill', models.ForeignKey(related_name='execution_apex_fill', to='main.ApexFill')),
                ('execution', models.OneToOneField(related_name='execution_apex_fill', to='main.Execution')),
            ],
        ),
        migrations.CreateModel(
            name='MarketOrderRequestAPEX',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderETNA',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('Price', models.FloatField()),
                ('Exchange', models.CharField(default='Auto', max_length=128)),
                ('TrailingLimitAmount', models.FloatField(default=0)),
                ('AllOrNone', models.IntegerField(default=0)),
                ('TrailingStopAmount', models.FloatField(default=0)),
                ('Type', models.IntegerField(choices=[(0, 'Market'), (1, 'Limit')], default=1)),
                ('Quantity', models.IntegerField()),
                ('SecurityId', models.IntegerField()),
                ('Side', models.IntegerField(choices=[(0, 'Buy'), (1, 'Sell')])),
                ('TimeInForce', models.IntegerField(choices=[(0, 'Day'), (1, 'GoodTillCancel'), (2, 'AtTheOpening'), (3, 'ImmediateOrCancel'), (4, 'FillOrKill'), (5, 'GoodTillCrossing'), (6, 'GoodTillDate')], default=6)),
                ('StopPrice', models.FloatField(default=0)),
                ('ExpireDate', models.IntegerField()),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('Order_Id', models.IntegerField(default=-1)),
                ('Status', models.CharField(choices=[('New', 'New'), ('Sent', 'Sent'), ('PartiallyFilled', 'PartiallyFilled'), ('Filled', 'Filled'), ('DoneForDay', 'DoneForDay'), ('Canceled', 'Canceled'), ('Replaced', 'Replaced'), ('PendingCancel', 'PendingCancel'), ('Stopped', 'Stopped'), ('Rejected', 'Rejected'), ('Suspended', 'Suspended'), ('PendingNew', 'PendingNew'), ('Calculated', 'Calculated'), ('Expired', 'Expired'), ('AcceptedForBidding', 'AcceptedForBidding'), ('PendingReplace', 'PendingReplace'), ('Error', 'Error'), ('Archived', 'Archived')], default='New', db_index=True, max_length=128)),
                ('FillPrice', models.FloatField(default=0)),
                ('FillQuantity', models.IntegerField(default=0)),
                ('Description', models.CharField(max_length=128)),
                ('fill_info', models.IntegerField(choices=[(0, 'FILLED'), (1, 'PARTIALY_FILLED'), (2, 'UNFILLED')], default=2)),
                ('ticker', models.ForeignKey(related_name='OrderETNA', on_delete=django.db.models.deletion.PROTECT, to='main.Ticker')),
            ],
        ),
        migrations.AddField(
            model_name='executiondistribution',
            name='execution_request',
            field=models.ForeignKey(default=None, related_name='execution_distributions', to='main.ExecutionRequest'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='accounttype',
            name='id',
            field=models.IntegerField(primary_key=True, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA'), (9, 'SEP IRA'), (10, '403K Account'), (11, 'SIMPLE IRA Account (Savings Incentive Match Plans for Employees)'), (12, 'SARSEP Account (Salary Reduction Simplified Employee Pension)'), (13, 'Payroll Deduction IRA Account'), (14, 'Profit-Sharing Account'), (15, 'Defined Benefit Account'), (16, 'Money Purchase Account'), (17, 'Employee Stock Ownership Account (ESOP)'), (18, 'Governmental Account'), (19, '457 Account'), (20, '409A Nonqualified Deferred Compensation Account'), (21, '403B Account'), (99, 'Other Account')], serialize=False),
        ),
        migrations.AddField(
            model_name='marketorderrequestapex',
            name='etna_order',
            field=models.ForeignKey(default=None, related_name='morsAPEX', to='main.OrderETNA'),
        ),
        migrations.AddField(
            model_name='marketorderrequestapex',
            name='market_order_request',
            field=models.ForeignKey(related_name='morsAPEX', to='main.MarketOrderRequest'),
        ),
        migrations.AddField(
            model_name='marketorderrequestapex',
            name='ticker',
            field=models.ForeignKey(related_name='morsAPEX', on_delete=django.db.models.deletion.PROTECT, to='main.Ticker'),
        ),
        migrations.AddField(
            model_name='apexfill',
            name='etna_order',
            field=models.ForeignKey(default=None, related_name='etna_fills', to='main.OrderETNA'),
        ),
        migrations.AlterUniqueTogether(
            name='marketorderrequestapex',
            unique_together=set([('ticker', 'market_order_request')]),
        ),
    ]
