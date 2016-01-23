# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20160123_0738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='from_account',
            field=models.ForeignKey(to='main.Goal', related_name='transactions_from', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='to_account',
            field=models.ForeignKey(to='main.Goal', related_name='transactions_to', blank=True, null=True),
        ),
    ]
