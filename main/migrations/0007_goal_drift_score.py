# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20160223_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='drift_score',
            field=models.FloatField(help_text='The maximum ratio of current drift to maximum allowable drift from any metric on this goal.', default=0.0),
        ),
    ]
