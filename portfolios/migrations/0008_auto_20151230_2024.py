# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0007_auto_20151201_1502'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proxyticker',
            options={'verbose_name': 'Ticker', 'verbose_name_plural': 'Tickers'},
        ),
    ]
