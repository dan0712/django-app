# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.CharField(default='PENDING', max_length=20, choices=[('PENDING', 'PENDING'), ('EXECUTED', 'EXECUTED')]),
        ),
    ]
