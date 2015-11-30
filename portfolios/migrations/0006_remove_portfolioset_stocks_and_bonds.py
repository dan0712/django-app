# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0005_portfolioset_stocks_and_bonds'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolioset',
            name='stocks_and_bonds',
        ),
    ]
