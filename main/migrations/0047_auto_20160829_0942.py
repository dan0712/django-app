# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20160824_1515'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assetclass',
            old_name='investment_type',
            new_name='investment_type_int',
        ),
    ]
