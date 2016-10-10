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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', models.FloatField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
