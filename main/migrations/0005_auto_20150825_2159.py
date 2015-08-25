# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20150825_2115'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticker',
            name='ordering',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='unit_price',
            field=models.FloatField(editable=False, default=1),
        ),
    ]
