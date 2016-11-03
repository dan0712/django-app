# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_auto_20161029_0227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalsetting',
            name='metric_group',
            field=models.ForeignKey(to='main.GoalMetricGroup', on_delete=django.db.models.deletion.PROTECT, related_name='settings'),
        ),
        migrations.AlterField(
            model_name='portfolioitem',
            name='asset',
            field=models.ForeignKey(to='main.Ticker', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
