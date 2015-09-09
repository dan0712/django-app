# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_platform_portfolio_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='account_type',
            field=models.CharField(default='INVESTING', max_length=20),
        ),
        migrations.AddField(
            model_name='goal',
            name='allocation',
            field=models.FloatField(default=0.4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goal',
            name='completion_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 9, 5, 53, 57, 407344, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goal',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 9, 9, 5, 54, 3, 919205, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goal',
            name='type',
            field=models.CharField(default='RETIREMENT', max_length=20),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(max_length=20, choices=[('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL')]),
        ),
    ]
