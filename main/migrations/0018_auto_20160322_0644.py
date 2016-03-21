# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20160322_0609'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField()),
                ('balance', models.FloatField()),
                ('goal', models.ForeignKey(to='main.Goal', related_name='balance_history')),
            ],
        ),
        migrations.RemoveField(
            model_name='portfolioset',
            name='tau',
        ),
    ]
