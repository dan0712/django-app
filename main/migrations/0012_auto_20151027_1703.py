# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0011_auto_20151026_0645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientaccount',
            name='account_class',
            field=models.CharField(max_length=20, default='trust_account',
                                   choices=[('joint_account', 'Personal Account'),
                                            ('trust_account', 'SMSF/Trust Account')]),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='account_group',
            field=models.ForeignKey(to='main.AccountGroup', related_name='accounts_all', null=True),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='primary_owner',
            field=models.ForeignKey(related_name='accounts_all', to='main.Client'),
        ),
    ]
