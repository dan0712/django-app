# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0003_portfolioset_name'),
        ('main', '0030_auto_20150909_1346'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='portfolio_set',
            field=models.ForeignKey(default=1, to='portfolios.PortfolioSet'),
            preserve_default=False,
        ),
    ]
