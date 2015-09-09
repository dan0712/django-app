# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0004_portfoliobyrisk'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfoliobyrisk',
            old_name='expectedReturn',
            new_name='expected_return',
        ),
    ]
