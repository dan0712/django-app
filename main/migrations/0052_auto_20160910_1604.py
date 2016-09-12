# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20160909_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='advisor',
            name='medicare_number',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='medicare_number',
        ),
    ]
