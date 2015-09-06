# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20150905_0856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientaccount',
            name='custom_fee',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='platform',
            name='fee',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
