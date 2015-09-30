# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150927_1029'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='dm_allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='dm_currency_hedge',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='dm_size',
        ),
    ]
