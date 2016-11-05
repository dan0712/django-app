# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_auto_20161028_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisor',
            name='geolocation_lock',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='geolocation_lock',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
