# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20151201_1224'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goal',
            old_name='picked_regions',
            new_name='custom_picked_regions',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='optimization_mode',
        ),
        migrations.AddField(
            model_name='goal',
            name='custom_optimization_mode',
            field=models.IntegerField(choices=[(0, 'None'), (1, 'auto mode'), (2, 'weight mode')], default=0),
        ),
    ]
