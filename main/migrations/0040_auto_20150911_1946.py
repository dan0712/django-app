# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_remove_goal_change_allocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionMemo',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('category', models.CharField(max_length=255)),
                ('comment', models.TextField()),
                ('transaction_type', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(max_length=20, choices=[('ALLOCATION', 'ALLOCATION'), ('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL')]),
        ),
        migrations.AddField(
            model_name='transactionmemo',
            name='transaction',
            field=models.ForeignKey(related_name='memos', to='main.Transaction'),
        ),
    ]
