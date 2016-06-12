# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20160607_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetclass',
            name='name',
            field=models.CharField(unique=True, max_length=255, validators=[django.core.validators.RegexValidator(regex='^[0-9A-Z_]+$', message='Invalid character only accept (0-9a-zA-Z_) ')]),
        ),
        migrations.AlterField(
            model_name='dailyprice',
            name='date',
            field=models.DateField(db_index=True),
        ),
        migrations.AlterField(
            model_name='dailyprice',
            name='instrument_object_id',
            field=models.PositiveIntegerField(null=True, db_index=True),
        ),
    ]
