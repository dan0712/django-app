# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160221_0705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='satelliteAlloc',
        ),
    ]
