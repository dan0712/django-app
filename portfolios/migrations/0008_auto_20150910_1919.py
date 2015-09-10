# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0007_auto_20150910_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliobyrisk',
            name='portfolio_set',
            field=models.ForeignKey(related_name='risk_profiles', to='portfolios.PortfolioSet'),
        ),
        migrations.AlterField(
            model_name='view',
            name='portfolio_set',
            field=models.ForeignKey(related_name='views', to='portfolios.PortfolioSet'),
        ),
    ]
