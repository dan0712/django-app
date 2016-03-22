# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20160322_0644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='reason',
            field=models.IntegerField(choices=[(0, 'DIVIDEND'), (1, 'DEPOSIT'), (2, 'WITHDRAWAL'), (3, 'REBALANCE'), (4, 'TRANSFER'), (5, 'FEE'), (6, 'ORDER'), (7, 'EXECUTION')], db_index=True),
        ),
    ]
