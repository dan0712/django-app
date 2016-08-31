# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_asset_class_changes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investmenttype',
            name='name',
            field=models.CharField(validators=[django.core.validators.RegexValidator(regex='^[0-9A-Z_]+$', message='Invalid character only accept (0-9a-zA-Z_) ')], unique=True, max_length=255),
        ),
    ]
