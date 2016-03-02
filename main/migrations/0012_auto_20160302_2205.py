# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20160302_2005'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecutionRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('reason', models.IntegerField(choices=[(0, 'Drift'), (1, 'Withdrawal'), (2, 'Deposit'), (3, 'Metric Change')])),
                ('volume', models.FloatField()),
                ('asset', models.ForeignKey(to='main.Ticker', related_name='execution_requests')),
                ('goal', models.ForeignKey(to='main.Goal', related_name='execution_requests')),
            ],
        ),
        migrations.CreateModel(
            name='MarketOrderRequest',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('account', models.ForeignKey(to='main.ClientAccount', related_name='market_orders')),
            ],
        ),
        migrations.AddField(
            model_name='executionrequest',
            name='order',
            field=models.ForeignKey(to='main.MarketOrderRequest', related_name='execution_requests'),
        ),
    ]
