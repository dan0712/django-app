# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_auto_20160219_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetclass',
            name='display_name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='display_order',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='name',
            field=models.CharField(db_index=True, max_length=255, validators=[django.core.validators.RegexValidator(message='Invalid character only accept (0-9a-zA-Z_) ', regex='^[0-9a-zA-Z_]+$')]),
        ),
        migrations.AlterField(
            model_name='goaltypes',
            name='name',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='display_name',
            field=models.CharField(db_index=True, max_length=255),
        )
    ]
