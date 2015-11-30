# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_goal_stocks_and_bonds'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='stocks_and_bonds',
        ),
    ]
