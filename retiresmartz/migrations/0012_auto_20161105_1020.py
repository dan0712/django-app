# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0011_auto_20161104_0253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='initial_deposits',
            field=jsonfield.fields.JSONField(help_text='List of deposits [{id, asset, goal, amt},...]', null=True, blank=True),
        ),
    ]
