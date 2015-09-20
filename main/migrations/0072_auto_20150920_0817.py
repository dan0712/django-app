# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0071_auto_20150920_0726'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialplanexternalaccount',
            name='account',
        ),
        migrations.AlterField(
            model_name='financialplanaccount',
            name='client',
            field=models.ForeignKey(to='main.Client', related_name='financial_plan_accounts'),
        ),
        migrations.AlterField(
            model_name='financialplanexternalaccount',
            name='client',
            field=models.ForeignKey(to='main.Client', related_name='financial_plan_external_accounts'),
        ),
    ]
