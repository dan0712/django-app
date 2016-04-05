# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20160404_2358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='rebalance',
        ),
        migrations.AddField(
            model_name='goalsetting',
            name='rebalance',
            field=models.BooleanField(help_text='Do we want to perform automated rebalancing?', default=True),
        ),
    ]
