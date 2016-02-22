# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20160222_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performer',
            name='group',
            field=models.CharField(max_length=20, default='PERFORMER_GROUP_BENCHMARK', choices=[('PERFORMER_GROUP_STRATEGY', 'PERFORMER_GROUP_STRATEGY'), ('PERFORMER_GROUP_BENCHMARK', 'PERFORMER_GROUP_BENCHMARK'), ('PERFORMER_GROUP_BOND', 'PERFORMER_GROUP_BOND'), ('PERFORMER_GROUP_STOCK', 'PERFORMER_GROUP_STOCK')]),
        ),
    ]
