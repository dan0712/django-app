# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0067_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderETNA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
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
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('Order_Id', models.IntegerField(default=-1)),
                ('Status', models.CharField(max_length=128, choices=[('New', 'New'), ('Sent', 'Sent'), ('PartiallyFilled', 'PartiallyFilled'), ('Filled', 'Filled'), ('DoneForDay', 'DoneForDay'), ('Canceled', 'Canceled'), ('Replaced', 'Replaced'), ('PendingCancel', 'PendingCancel'), ('Stopped', 'Stopped'), ('Rejected', 'Rejected'), ('Suspended', 'Suspended'), ('PendingNew', 'PendingNew'), ('Calculated', 'Calculated'), ('Expired', 'Expired'), ('AcceptedForBidding', 'AcceptedForBidding'), ('PendingReplace', 'PendingReplace'), ('Error', 'Error')], default='New', db_index=True)),
                ('FillPrice', models.FloatField(default=0)),
                ('FillQuantity', models.IntegerField(default=0)),
                ('Description', models.CharField(max_length=128)),
                ('fill_info', models.IntegerField(choices=[(0, 'FILLED'), (1, 'PARTIALY_FILLED'), (2, 'UNFILLED')], default=2)),
                ('ticker', models.ForeignKey(related_name='OrderETNA', to='main.Ticker', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
    ]
