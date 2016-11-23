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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('price', models.FloatField(help_text='Price for the fill.')),
                ('executed', models.DateTimeField(help_text='The time the trade was executed.')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionApexFill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('apex_fill', models.ForeignKey(related_name='execution_apex_fill', to='main.ApexFill')),
                ('execution', models.OneToOneField(to='main.Execution', related_name='execution_apex_fill')),
            ],
        ),
        migrations.CreateModel(
            name='MarketOrderRequestAPEX',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderETNA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Price', models.FloatField()),
                ('Exchange', models.CharField(max_length=128, default='Auto')),
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
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('Order_Id', models.IntegerField(default=-1)),
                ('Status', models.CharField(db_index=True, max_length=128, choices=[('New', 'New'), ('Sent', 'Sent'), ('PartiallyFilled', 'PartiallyFilled'), ('Filled', 'Filled'), ('DoneForDay', 'DoneForDay'), ('Canceled', 'Canceled'), ('Replaced', 'Replaced'), ('PendingCancel', 'PendingCancel'), ('Stopped', 'Stopped'), ('Rejected', 'Rejected'), ('Suspended', 'Suspended'), ('PendingNew', 'PendingNew'), ('Calculated', 'Calculated'), ('Expired', 'Expired'), ('AcceptedForBidding', 'AcceptedForBidding'), ('PendingReplace', 'PendingReplace'), ('Error', 'Error'), ('Archived', 'Archived')], default='New')),
                ('FillPrice', models.FloatField(default=0)),
                ('FillQuantity', models.IntegerField(default=0)),
                ('Description', models.CharField(max_length=128)),
                ('fill_info', models.IntegerField(choices=[(0, 'FILLED'), (1, 'PARTIALY_FILLED'), (2, 'UNFILLED')], default=2)),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='OrderETNA', to='main.Ticker')),
            ],
        ),
        migrations.AddField(
            model_name='executiondistribution',
            name='execution_request',
            field=models.ForeignKey(null=True, related_name='execution_distributions', blank=True, to='main.ExecutionRequest'),
        ),
        migrations.AlterField(
            model_name='accounttype',
            name='id',
            field=models.IntegerField(serialize=False, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (24, 'Investment Club Account'), (25, 'Partnership/Limited partnership Account'), (26, 'Sole Proprietor Account'), (27, 'Limited Liability Company Account'), (28, 'Association Account'), (29, 'Non-corporate organization Account'), (30, 'Pension Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA'), (9, 'SEP IRA'), (10, '403K Account'), (11, 'SIMPLE IRA Account (Savings Incentive Match Plans for Employees)'), (12, 'SARSEP Account (Salary Reduction Simplified Employee Pension)'), (13, 'Payroll Deduction IRA Account'), (14, 'Profit-Sharing Account'), (16, 'Money Purchase Account'), (17, 'Employee Stock Ownership Account (ESOP)'), (18, 'Governmental Account'), (19, '457 Account'), (20, '409A Nonqualified Deferred Compensation Account'), (21, '403B Account'), (31, 'Health Savings Account'), (32, '529 college savings plans Account'), (33, 'Coverdell Educational Savings Account (ESA) Account'), (34, 'UGMA/UTMA Account'), (35, 'Guardianship of the Estate Account'), (36, 'Custodial Account'), (37, 'Thrift Savings Account')], primary_key=True),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='morsAPEX', to='main.Ticker'),
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
