# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_goal_total_balance_db'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisor',
            name='work_phone',
            field=django_localflavor_au.models.AUPhoneNumberField(null=True, max_length=10),
        ),
        migrations.AddField(
            model_name='client',
            name='medicare_number',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='address_line_2',
            field=models.CharField(blank=True, null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('REBALANCE', 'REBALANCE'), ('ALLOCATION', 'ALLOCATION'), ('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL')], max_length=20),
        ),
    ]
