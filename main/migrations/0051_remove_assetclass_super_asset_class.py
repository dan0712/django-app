# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_remove_assetclass_investment_type_int'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assetclass',
            name='super_asset_class',
        ),
    ]
