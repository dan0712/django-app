# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0074_financialplan_income_replacement_ratio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='target',
            field=models.FloatField(default=0),
        ),
    ]
