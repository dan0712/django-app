# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0004_auto_20160926_2230'),
    ]

    operations = [
        migrations.CreateModel(
            name='InflationForecast',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='InflationForecastImport',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Date the forecast been made on.')),
                ('csv_file', models.FileField(upload_to='', help_text='CSV file with one column of values starting the `date`.')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='inflationforecast',
            name='imported',
            field=models.ForeignKey(to='retiresmartz.InflationForecastImport'),
        ),
    ]
