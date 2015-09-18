# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_auto_20150918_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='target',
            field=models.FloatField(null=True),
        ),
    ]
