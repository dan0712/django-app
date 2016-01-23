# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='last_action',
            field=models.DateTimeField(null=True),
        ),
    ]
