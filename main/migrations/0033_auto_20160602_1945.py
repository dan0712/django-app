# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20160511_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetclass',
            name='display_name',
            field=models.CharField(max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='investment_type',
            field=models.CharField(choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS'), ('MIXED', 'MIXED')], max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='assetclass',
            name='super_asset_class',
            field=models.CharField(choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('EQUITY_INT', 'EQUITY_INT'), ('EQUITY_UK', 'EQUITY_UK'), ('EQUITY_JAPAN', 'EQUITY_JAPAN'), ('EQUITY_AS', 'EQUITY_AS'), ('EQUITY_CN', 'EQUITY_CN'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT'), ('FIXED_INCOME_UK', 'FIXED_INCOME_UK'), ('FIXED_INCOME_JAPAN', 'FIXED_INCOME_JAPAN'), ('FIXED_INCOME_AS', 'FIXED_INCOME_AS'), ('FIXED_INCOME_CN', 'FIXED_INCOME_CN')], max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='employment_status',
            field=models.IntegerField(choices=[(0, 'Employed (full-time)'), (1, 'Employed (part-time)'), (2, 'Self-employed'), (3, 'Student'), (4, 'Retired'), (5, 'Homemaker'), (6, 'Not employed')], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='user',
            field=models.OneToOneField(related_name='client', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='can_write',
            field=models.BooleanField(default=False, verbose_name='Has Full Access?', help_text="A supervisor with 'full access' can impersonate advisers and clients and make any action as them."),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(verbose_name='last name', max_length=30, db_index=True),
        ),
    ]
