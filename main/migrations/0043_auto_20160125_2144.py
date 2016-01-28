# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetFeature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, help_text="This should be a noun such as 'Region'.", max_length=127)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetFeatureValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, help_text='This should be an adjective.', max_length=127)),
                ('description', models.TextField(null=True, help_text='A clarification of what this value means.', blank=True)),
                ('assets', models.ManyToManyField(related_name='features', to='main.Ticker')),
                ('feature', models.ForeignKey(help_text='The asset feature this is one value for.', related_name='values', to='main.AssetFeature')),
            ],
        ),
        migrations.RemoveField(
            model_name='assetgroup',
            name='assets',
        ),
        migrations.RemoveField(
            model_name='goalmetric',
            name='group',
        ),
        migrations.AddField(
            model_name='goalmetric',
            name='comparison',
            field=models.IntegerField(choices=[(0, 'Minimum'), (1, 'Exactly'), (2, 'Maximum')], default=1),
        ),
        migrations.AlterField(
            model_name='goal',
            name='account',
            field=models.ForeignKey(related_name='all_goals', to='main.ClientAccount'),
        ),
        migrations.DeleteModel(
            name='AssetGroup',
        ),
        migrations.AddField(
            model_name='goalmetric',
            name='feature',
            field=models.ForeignKey(null=True, to='main.AssetFeatureValue'),
        ),
    ]
