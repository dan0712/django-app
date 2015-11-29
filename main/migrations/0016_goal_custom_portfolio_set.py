# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0003_auto_20151007_1446'),
        ('main', '0015_auto_20151127_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='custom_portfolio_set',
            field=models.ForeignKey(to='portfolios.PortfolioSet', null=True, blank=True),
        ),
    ]
