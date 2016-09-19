# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_ticker_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='PositionLot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('quantity', models.FloatField(null=True, default=None, blank=True)),
                ('execution_distribution', models.ForeignKey(unique=True, to='main.ExecutionDistribution', related_name='position_lot')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('quantity', models.FloatField(null=True, default=None, blank=True)),
                ('execution_distribution', models.ForeignKey(unique=True, to='main.ExecutionDistribution', related_name='sold_lot')),
            ],
        ),
    ]
