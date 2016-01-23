# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_dividend'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetFee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=127)),
                ('applied_per', models.IntegerField(choices=[(0, 'Day End'), (1, 'Complete Day'), (2, 'Month End'), (3, 'Complete Month'), (4, 'Fiscal Month End'), (5, 'Entry Order'), (6, 'Entry Order Item'), (7, 'Exit Order'), (8, 'Exit Order Item'), (9, 'Transaction')])),
                ('fixed_level_unit', models.IntegerField(choices=[(0, 'Asset Value'), (1, 'Asset Qty'), (2, 'NAV Performance')])),
                ('fixed_level_type', models.IntegerField(choices=[(0, 'Add'), (1, 'Replace')])),
                ('fixed_levels', models.TextField(help_text="List of level transition points and the new values after that transition. Eg. '0: 0.001, 10000: 0.0'")),
                ('prop_level_unit', models.IntegerField(choices=[(0, 'Asset Value'), (1, 'Asset Qty'), (2, 'NAV Performance')])),
                ('prop_apply_unit', models.IntegerField(choices=[(0, 'Asset Value'), (1, 'Asset Qty'), (2, 'NAV Performance')])),
                ('prop_level_type', models.IntegerField(choices=[(0, 'Add'), (1, 'Replace')])),
                ('prop_levels', models.TextField(help_text="List of level transition points and the new values after that transition. Eg. '0: 0.001, 10000: 0.0'")),
                ('asset', models.ForeignKey(to='main.Ticker')),
            ],
        ),
        migrations.CreateModel(
            name='AssetFeePlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=127)),
                ('description', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=127)),
            ],
        ),
        migrations.CreateModel(
            name='FiscalYear',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=127)),
                ('year', models.IntegerField()),
                ('begin_date', models.DateField(help_text='Inclusive begin date for this fiscal year')),
                ('end_date', models.DateField(help_text='Inclusive end date for this fiscal year')),
                ('month_ends', models.CommaSeparatedIntegerField(help_text='Comma separated month end days each month of the year. First element is January.', max_length=35, validators=[django.core.validators.MinLengthValidator(23)])),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='dividend',
            unique_together=set([('instrument', 'record_date')]),
        ),
        migrations.AddField(
            model_name='company',
            name='fiscal_years',
            field=models.ManyToManyField(to='main.FiscalYear'),
        ),
        migrations.AddField(
            model_name='assetfee',
            name='collector',
            field=models.ForeignKey(to='main.Company'),
        ),
        migrations.AddField(
            model_name='assetfee',
            name='plan',
            field=models.ForeignKey(to='main.AssetFeePlan'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='asset_fee_plan',
            field=models.ForeignKey(to='main.AssetFeePlan', null=True),
        ),
    ]
