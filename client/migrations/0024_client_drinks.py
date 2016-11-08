# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0023_client_geolocation_lock'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='drinks',
            field=models.PositiveIntegerField(null=True, blank=True, help_text='Number of drinks per week'),
        ),
    ]
