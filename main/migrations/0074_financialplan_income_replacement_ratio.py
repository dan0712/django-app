# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0073_remove_financialplan_income_replacement_ratio'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialplan',
            name='income_replacement_ratio',
            field=models.FloatField(null=True),
        ),
    ]
