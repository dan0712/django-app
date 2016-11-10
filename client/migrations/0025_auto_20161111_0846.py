# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0024_client_drinks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='drinks',
            field=models.PositiveIntegerField(blank=True, null=True, help_text='Number of drinks per day'),
        ),
        migrations.AlterField(
            model_name='client',
            name='height',
            field=models.FloatField(blank=True, null=True, help_text='In centimeters'),
        ),
        migrations.AlterField(
            model_name='client',
            name='weight',
            field=models.FloatField(blank=True, null=True, help_text='In kilograms'),
        ),
    ]
