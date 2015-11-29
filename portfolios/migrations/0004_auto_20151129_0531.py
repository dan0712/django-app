# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0003_auto_20151007_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfoliobyrisk',
            name='portfolio_set',
        ),
        migrations.AddField(
            model_name='portfolioset',
            name='default_region_sizes',
            field=models.TextField(default='{}'),
        ),
        migrations.AddField(
            model_name='portfolioset',
            name='portfolios',
            field=models.TextField(null=True, blank=True, editable=False),
        ),
        migrations.DeleteModel(
            name='PortfolioByRisk',
        ),
    ]
