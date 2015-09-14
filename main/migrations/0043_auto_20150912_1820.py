# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_automaticdeposit'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='executed_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(max_length=20, choices=[('FEE', 'FEE'), ('ALLOCATION', 'ALLOCATION'), ('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL')]),
        ),
    ]
