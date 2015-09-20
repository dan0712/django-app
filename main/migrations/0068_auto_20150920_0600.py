# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0067_auto_20150920_0550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialplan',
            name='income_replacement_ratio',
            field=models.CharField(null=True, max_length=100),
        ),
    ]
