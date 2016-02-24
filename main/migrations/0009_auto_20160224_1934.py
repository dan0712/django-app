# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20160224_0331'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfolio',
            old_name='created_date',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='created_date',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='executed_date',
            new_name='executed',
        ),
    ]
