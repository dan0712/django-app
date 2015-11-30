# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0004_auto_20151129_0531'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioset',
            name='stocks_and_bonds',
            field=models.TextField(default='both'),
        ),
    ]
