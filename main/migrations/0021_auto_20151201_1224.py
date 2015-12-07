# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_remove_goal_stocks_and_bonds'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='optimization_mode',
            field=models.IntegerField(choices=[(0, "None"), (1, 'auto mode'), (2, 'weight mode')], default=0),
        ),
        migrations.AddField(
            model_name='goal',
            name='picked_regions',
            field=models.TextField(null=True),
        ),
    ]
