# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20151201_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='custom_hedges',
            field=models.TextField(null=True),
        ),
    ]
