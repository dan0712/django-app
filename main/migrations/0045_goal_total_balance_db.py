# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20150915_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='total_balance_db',
            field=models.FloatField(default=0, verbose_name='total balance'),
        ),
    ]
