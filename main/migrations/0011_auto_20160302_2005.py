# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_add_metric_group_20160225_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='rebalance',
            field=models.BooleanField(help_text='Do we want to perform automated rebalancing on this goal?', default=True),
        ),
    ]
