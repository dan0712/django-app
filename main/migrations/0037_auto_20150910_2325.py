# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_ticker_currency'),
    ]

    operations = [
        migrations.RenameField(
            model_name='position',
            old_name='value',
            new_name='share',
        ),
    ]
