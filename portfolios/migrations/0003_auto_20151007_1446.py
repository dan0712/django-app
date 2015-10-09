# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0002_marketcap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marketcap',
            name='ticker',
            field=models.OneToOneField(related_name='market_cap', to='main.Ticker'),
        ),
    ]
