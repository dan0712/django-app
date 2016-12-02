# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0031_auto_20161201_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='civil_status',
            field=models.IntegerField(null=True, choices=[(0, 'Not Married'), (1, 'Married')]),
        ),
    ]
