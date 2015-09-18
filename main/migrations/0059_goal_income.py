# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_auto_20150918_2101'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='income',
            field=models.BooleanField(default=False),
        ),
    ]
