# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20150909_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientaccount',
            name='account_type',
            field=models.CharField(choices=[('PERSONAL', 'Personal Account')], default='PERSONAL', max_length=20),
        ),
        migrations.AlterField(
            model_name='position',
            name='value',
            field=models.FloatField(),
        ),
    ]
