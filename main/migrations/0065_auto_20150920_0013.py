# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_auto_20150920_0010'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialprofile',
            name='spouse_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
