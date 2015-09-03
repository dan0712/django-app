# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20150903_0840'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountgroup',
            name='name',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='account_group',
            field=models.ForeignKey(to='main.AccountGroup', null=True, related_name='accounts'),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='custom_fee',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
