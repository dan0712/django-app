# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0061_auto_20161009_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
