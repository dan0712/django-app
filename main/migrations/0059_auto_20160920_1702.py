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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('quantity', models.FloatField(null=True, default=None, blank=True)),
                ('execution_distribution', models.OneToOneField(to='main.ExecutionDistribution', related_name='position_lot')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('quantity', models.FloatField(null=True, default=None, blank=True)),
                ('buy_execution_distribution', models.OneToOneField(to='main.ExecutionDistribution', related_name='bought_lot')),
                ('sell_execution_distribution', models.OneToOneField(to='main.ExecutionDistribution', related_name='sold_lot')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='position',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='position',
            name='goal',
        ),
        migrations.RemoveField(
            model_name='position',
            name='ticker',
        ),
        migrations.DeleteModel(
            name='Position',
        ),
    ]
