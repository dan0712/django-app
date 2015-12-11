# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_goal_custom_hedges'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='satellite_pct',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], default=0.0, null=True),
        ),
    ]
