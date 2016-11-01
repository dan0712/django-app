# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0009_auto_20161028_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='calculated_life_expectancy',
            field=models.PositiveIntegerField(editable=False, blank=True, default=85),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='max_risk',
            field=models.FloatField(editable=False, blank=True, help_text='The maximum allowable risk appetite for this retirement plan, based on our risk model', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='recommended_risk',
            field=models.FloatField(editable=False, blank=True, help_text='The calculated recommended risk for this retirement plan', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
