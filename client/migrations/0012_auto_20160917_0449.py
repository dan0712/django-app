# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0011_auto_20160910_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='daily_exercise',
            field=models.PositiveIntegerField(null=True, blank=True, help_text='In Minutes'),
        ),
        migrations.AddField(
            model_name='client',
            name='height',
            field=models.PositiveIntegerField(default=0, help_text='In centimeters'),
        ),
        migrations.AddField(
            model_name='client',
            name='smoker',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='client',
            name='weight',
            field=models.PositiveIntegerField(default=0, help_text='In kilograms'),
        ),
    ]
