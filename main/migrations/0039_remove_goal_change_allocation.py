# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_goal_change_allocation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='change_allocation',
        ),
    ]
