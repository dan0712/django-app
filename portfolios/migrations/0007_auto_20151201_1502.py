# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0006_remove_portfolioset_stocks_and_bonds'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioset',
            name='default_picked_regions',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='portfolioset',
            name='optimization_mode',
            field=models.IntegerField(choices=[(1, 'auto mode'), (2, 'weight mode')], default=2),
        ),
    ]
