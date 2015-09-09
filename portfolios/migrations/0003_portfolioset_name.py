# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0002_portfolioset'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioset',
            name='name',
            field=models.CharField(max_length=100, default=1),
            preserve_default=False,
        ),
    ]
