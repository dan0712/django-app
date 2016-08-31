# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0004_remove_client_net_worth'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientaccount',
            name='account_id',
            field=models.CharField(default='UNSET', max_length=10),
            preserve_default=False,
        ),
    ]
