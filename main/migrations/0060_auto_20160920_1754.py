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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('quantity', models.FloatField(blank=True, null=True, default=None)),
                ('execution_distribution', models.OneToOneField(related_name='position_lot', to='main.ExecutionDistribution')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('quantity', models.FloatField(blank=True, null=True, default=None)),
                ('buy_execution_distribution', models.OneToOneField(related_name='bought_lot', to='main.ExecutionDistribution')),
                ('sell_execution_distribution', models.OneToOneField(related_name='sold_lot', to='main.ExecutionDistribution')),
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
