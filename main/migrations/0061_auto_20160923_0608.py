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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
            ],
        ),
        migrations.CreateModel(
            name='ApexOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('ticker', models.ForeignKey(to='main.Ticker', related_name='apex_order', on_delete=django.db.models.deletion.PROTECT)),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionApexFill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('apex_fill', models.ForeignKey(related_name='execution_apex_fill', to='main.ApexFill')),
                ('execution', models.OneToOneField(to='main.Execution', related_name='execution_apex_fill')),
            ],
        ),
        migrations.CreateModel(
            name='MarketOrderRequestAPEX',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('apex_order', models.ForeignKey(related_name='morAPEX', to='main.ApexOrder')),
                ('market_order_request', models.ForeignKey(related_name='morAPEX', to='main.MarketOrderRequest')),
            ],
        ),
        migrations.AddField(
            model_name='executiondistribution',
            name='execution_request',
            field=models.OneToOneField(to='main.ExecutionRequest', related_name='execution_distribution', default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='apexfill',
            name='apex_order',
            field=models.ForeignKey(related_name='apex_fill', to='main.ApexOrder'),
        ),
    ]
