# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_auto_20150916_0452'),
    ]

    operations = [
        migrations.CreateModel(
            name='Performer',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('symbol', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=100)),
                ('group', models.CharField(max_length=20, choices=[('STRATEGY', 'STRATEGY'), ('BENCHMARK', 'BENCHMARK'), ('BOND', 'BOND'), ('STOCK', 'STOCK')], default='BENCHMARK')),
                ('allocation', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SymbolHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('price', models.FloatField()),
                ('symbol', models.CharField(max_length=20)),
                ('date', models.DateField()),
            ],
        ),
    ]
