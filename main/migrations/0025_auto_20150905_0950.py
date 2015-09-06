# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_auto_20150905_0932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firm',
            name='fee',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
