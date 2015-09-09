# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_transaction_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(related_name='transactions', to='main.Goal'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='from_account',
            field=models.ForeignKey(blank=True, null=True, related_name='transactions_from', to='main.Goal'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='to_account',
            field=models.ForeignKey(blank=True, null=True, related_name='transactions_to', to='main.Goal'),
        ),
    ]
