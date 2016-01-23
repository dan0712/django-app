# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20160123_2315'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=127)),
                ('assets', models.ManyToManyField(to='main.Ticker', related_name='asset_groups')),
            ],
        ),
        migrations.CreateModel(
            name='GoalMetric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('type', models.IntegerField(choices=[(0, 'Portfolio Mix'), (1, 'RiskScore')])),
                ('rebalance_type', models.IntegerField(help_text='Is the rebalance threshold an absolute threshold or relative (percentage difference) threshold?', choices=[(0, 'Absolute'), (1, 'Relative')])),
                ('rebalance_thr', models.FloatField(help_text='The difference between configured and measured value at which a rebalance will be recommended.')),
                ('configured_val', models.FloatField(help_text='The value of the metric that was configured.')),
                ('measured_val', models.FloatField(help_text='The latest measured value of the metric', null=True)),
                ('goal', models.ForeignKey(related_name='metrics', to='main.Goal')),
                ('group', models.ForeignKey(to='main.AssetGroup', null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='assetfeeplan',
            name='name',
            field=models.CharField(unique=True, max_length=127),
        ),
    ]
