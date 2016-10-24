# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0005_retirementadvice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='calculated_life_expectancy',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
