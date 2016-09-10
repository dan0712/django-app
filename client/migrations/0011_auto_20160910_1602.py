# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0010_auto_20160909_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='associated_to_broker_dealer',
        ),
        migrations.RemoveField(
            model_name='client',
            name='medicare_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='provide_tfn',
        ),
        migrations.RemoveField(
            model_name='client',
            name='public_position_insider',
        ),
        migrations.RemoveField(
            model_name='client',
            name='tax_file_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='ten_percent_insider',
        ),
        migrations.RemoveField(
            model_name='client',
            name='us_citizen',
        ),
    ]
