# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='PositionLot',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('quantity', models.FloatField(blank=True, null=True, default=None)),
                ('execution_distribution', models.OneToOneField(to='main.ExecutionDistribution', related_name='position_lot')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('quantity', models.FloatField(blank=True, null=True, default=None)),
                ('buy_execution_distribution', models.ForeignKey(to='main.ExecutionDistribution', related_name='bought_lot')),
                ('sell_execution_distribution', models.ForeignKey(to='main.ExecutionDistribution', related_name='sold_lot')),
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
