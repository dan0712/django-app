# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0004_auto_20150929_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='dm_allocation',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='goal',
            name='dm_currency_hedge',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='goal',
            name='dm_size',
            field=models.FloatField(default=0.5),
        ),
        migrations.AlterField(
            model_name='goal',
            name='au_size',
            field=models.FloatField(default=0.5),
        ),
    ]
