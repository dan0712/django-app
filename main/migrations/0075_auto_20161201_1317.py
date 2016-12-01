# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0074_auto_20161123_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='civil_status',
            field=models.IntegerField(choices=[(0, 'SINGLE'), (1, 'MARRIED_FILING_JOINTLY'), (2, 'MARRIED_FILING_SEPARATELY_LIVED_TOGETHER'), (3, 'MARRIED_FILING_SEPARATELY_NOT_LIVED_TOGETHER'), (4, 'HEAD_OF_HOUSEHOLD'), (5, 'QUALIFYING_WIDOWER')], null=True),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='civil_status',
            field=models.IntegerField(choices=[(0, 'SINGLE'), (1, 'MARRIED_FILING_JOINTLY'), (2, 'MARRIED_FILING_SEPARATELY_LIVED_TOGETHER'), (3, 'MARRIED_FILING_SEPARATELY_NOT_LIVED_TOGETHER'), (4, 'HEAD_OF_HOUSEHOLD'), (5, 'QUALIFYING_WIDOWER')], null=True),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='can_write',
            field=models.BooleanField(help_text="A supervisor with 'full access' can perform actions for their advisors and clients.", default=False, verbose_name='Has Full Access?'),
        ),
    ]
