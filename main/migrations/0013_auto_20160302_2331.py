# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20160302_2205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolioset',
            name='default_picked_regions',
        ),
        migrations.RemoveField(
            model_name='portfolioset',
            name='default_region_sizes',
        ),
        migrations.RemoveField(
            model_name='portfolioset',
            name='optimization_mode',
        ),
        migrations.RemoveField(
            model_name='portfolioset',
            name='portfolios',
        ),
    ]
