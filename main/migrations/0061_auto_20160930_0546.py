# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0060_auto_20160921_0422'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApexFill',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('price', models.FloatField(help_text='Price for the fill.')),
                ('executed', models.DateTimeField(help_text='The time the trade was executed.')),
            ],
        ),
        migrations.CreateModel(
            name='ApexOrder',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('state', models.IntegerField(choices=[(0, 'PENDING'), (1, 'APPROVED'), (2, 'SENT'), (3, 'CANCEL_PENDING'), (4, 'COMPLETE')], default=0)),
                ('fill_info', models.IntegerField(choices=[(0, 'FILLED'), (1, 'PARTIALY_FILLED'), (2, 'UNFILLED')], default=2)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Ticker', related_name='apex_orders')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionApexFill',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('apex_fill', models.ForeignKey(related_name='execution_apex_fill', to='main.ApexFill')),
                ('execution', models.OneToOneField(to='main.Execution', related_name='execution_apex_fill')),
            ],
        ),
        migrations.CreateModel(
            name='MarketOrderRequestAPEX',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('apex_order', models.ForeignKey(related_name='morsAPEX', to='main.ApexOrder')),
                ('market_order_request', models.ForeignKey(related_name='morsAPEX', to='main.MarketOrderRequest')),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.Ticker', related_name='morsAPEX')),
            ],
        ),
        migrations.AddField(
            model_name='executiondistribution',
            name='execution_request',
            field=models.ForeignKey(to='main.ExecutionRequest', related_name='execution_distributions', default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='apexfill',
            name='apex_order',
            field=models.ForeignKey(related_name='apex_fills', to='main.ApexOrder'),
        ),
        migrations.AlterUniqueTogether(
            name='marketorderrequestapex',
            unique_together=set([('ticker', 'market_order_request')]),
        ),
    ]
