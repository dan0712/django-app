# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0009_auto_20151022_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientaccount',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='token',
            field=models.CharField(max_length=36, default='', editable=False),
            preserve_default=False,
        ),
    ]
