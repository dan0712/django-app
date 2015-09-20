# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0072_auto_20150920_0817'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialplan',
            name='income_replacement_ratio',
        ),
    ]
