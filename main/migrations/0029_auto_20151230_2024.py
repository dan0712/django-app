# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_merge'),
    ]

    operations = [

        migrations.AlterField(
            model_name='ticker',
            name='region',
            field=models.ForeignKey(to='main.Region'),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='symbol',
            field=models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid symbol format', regex='^[^ ]+$')], max_length=10, unique=True),
        ),
    ]
