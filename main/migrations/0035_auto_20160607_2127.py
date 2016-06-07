# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20160607_0124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supervisor',
            name='can_write',
            field=models.BooleanField(help_text="A supervisor with 'full access' can perform actions for their advisers and clients.", default=False, verbose_name='Has Full Access?'),
        ),
    ]
