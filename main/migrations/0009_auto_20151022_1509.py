# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_clientaccount_account_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='advisor',
            field=models.ForeignKey(to='main.Advisor', related_name='all_clients'),
        ),
    ]
