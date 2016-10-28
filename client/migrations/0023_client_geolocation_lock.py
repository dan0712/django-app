# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0022_auto_20161023_0843'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='geolocation_lock',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
