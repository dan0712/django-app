# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0029_auto_20161122_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='civil_status',
            field=models.IntegerField(choices=[(0, 'SINGLE'), (1, 'MARRIED_FILING_JOINTLY'), (2, 'MARRIED_FILING_SEPARATELY_LIVED_TOGETHER'), (3, 'MARRIED_FILING_SEPARATELY_NOT_LIVED_TOGETHER'), (4, 'HEAD_OF_HOUSEHOLD'), (5, 'QUALIFYING_WIDOWER')], null=True),
        ),
    ]
