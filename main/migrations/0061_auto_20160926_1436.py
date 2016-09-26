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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
            ],
        ),
        migrations.CreateModel(
            name='ApexOrder',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('ticker', models.ForeignKey(to='main.Ticker', related_name='apex_orders', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionApexFill',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('apex_fill', models.ForeignKey(to='main.ApexFill', related_name='execution_apex_fill')),
                ('execution', models.OneToOneField(to='main.Execution', related_name='execution_apex_fill')),
            ],
        ),
        migrations.CreateModel(
            name='MarketOrderRequestAPEX',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('apex_order', models.ForeignKey(to='main.ApexOrder', related_name='morsAPEX')),
                ('market_order_request', models.ForeignKey(to='main.MarketOrderRequest', related_name='morsAPEX')),
                ('ticker', models.ForeignKey(to='main.Ticker', related_name='morsAPEX', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.AddField(
            model_name='executiondistribution',
            name='execution_request',
            field=models.OneToOneField(to='main.ExecutionRequest', default=None, related_name='execution_distribution'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='apexfill',
            name='apex_order',
            field=models.ForeignKey(to='main.ApexOrder', related_name='apex_fills'),
        ),
        migrations.AlterUniqueTogether(
            name='marketorderrequestapex',
            unique_together=set([('ticker', 'market_order_request')]),
        ),
    ]
