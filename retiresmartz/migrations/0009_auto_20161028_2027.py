# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0008_retirementplan_same_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='expected_return_confidence',
            field=models.FloatField(help_text='Planned confidence of the portfolio returns given the volatility and risk predictions.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
