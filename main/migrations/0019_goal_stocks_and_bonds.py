# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_firm_can_use_ethical_portfolio'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='stocks_and_bonds',
            field=models.TextField(default='both'),
        ),
    ]
