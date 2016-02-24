# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_goal_drift_score'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfolio',
            old_name='variance',
            new_name='stdev',
        ),
    ]
