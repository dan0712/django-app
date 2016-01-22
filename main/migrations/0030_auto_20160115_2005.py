# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20151230_2024'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyPrice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('date', models.DateField()),
                ('nav', models.FloatField(null=True)),
                ('aum', models.BigIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('first', models.CharField(max_length=3)),
                ('second', models.CharField(max_length=3)),
                ('date', models.DateField()),
                ('rate', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='ticker',
            name='data_api',
            field=models.CharField(help_text='The module that will be used to get the data for this ticker', max_length=30, choices=[('portfolios.api.bloomberg', 'Bloomberg')], null=True),
        ),
        migrations.AddField(
            model_name='ticker',
            name='data_api_param',
            field=models.CharField(help_text='Structured parameter string appropriate for the data api. The first component would probably be id appropriate for the given api', max_length=30, unique=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='monthlyprices',
            unique_together=set([('symbol', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='exchangerate',
            unique_together=set([('first', 'second', 'date')]),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='ticker',
            field=models.ForeignKey(db_index=False, to='main.Ticker'),
        ),
        migrations.AlterUniqueTogether(
            name='dailyprice',
            unique_together=set([('ticker', 'date')]),
        ),
    ]
