# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_auto_20160708_2316'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'addresses', 'verbose_name': 'address'},
        ),
        migrations.AlterModelOptions(
            name='region',
            options={'verbose_name_plural': 'regions', 'verbose_name': 'region'},
        ),
    ]
