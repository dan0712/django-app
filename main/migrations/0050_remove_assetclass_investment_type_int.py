# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_data_migration_investmenttype_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assetclass',
            name='investment_type_int',
        ),
    ]
