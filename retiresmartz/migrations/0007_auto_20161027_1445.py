# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0006_auto_20161025_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='name',
            field=models.CharField(blank=True, null=True, max_length=128),
        ),
    ]
