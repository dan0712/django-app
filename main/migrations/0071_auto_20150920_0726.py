# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0070_auto_20150920_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialplanaccount',
            name='account',
            field=models.ForeignKey(to='main.Goal'),
        ),
    ]
