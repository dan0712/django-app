# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20160321_2303'),
    ]

    operations = [
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('volume', models.FloatField(help_text='Will be negative for a sell.')),
                ('price', models.FloatField(help_text='The raw price paid/received per share. Not including fees etc.')),
                ('executed', models.DateTimeField(help_text='The time the trade was executed.')),
                ('amount', models.FloatField(help_text='The realised amount that was transferred into the account (specified on the order) taking into account external fees etc.')),
                ('asset', models.ForeignKey(related_name='executions', to='main.Ticker')),
            ],
        ),
        migrations.CreateModel(
            name='ExecutionDistribution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('volume', models.FloatField(help_text='The number of units from the execution that were applied to the transaction.')),
                ('execution', models.ForeignKey(related_name='distributions', to='main.Execution')),
            ],
        ),
        migrations.AddField(
            model_name='executionrequest',
            name='transaction',
            field=models.OneToOneField(null=True, related_name='execution_request', to='main.Transaction'),
        ),
        migrations.AddField(
            model_name='marketorderrequest',
            name='state',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Approved'), (2, 'Sent'), (3, 'Complete')], default=0),
        ),
        migrations.AlterField(
            model_name='executionrequest',
            name='volume',
            field=models.FloatField(help_text='Will be negative for a sell.'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='reason',
            field=models.IntegerField(choices=[(0, 'DIVIDEND'), (1, 'DEPOSIT'), (2, 'WITHDRAWAL'), (3, 'REBALANCE'), (4, 'TRANSFER'), (5, 'FEE'), (6, 'ORDER'), (6, 'EXECUTION')], db_index=True),
        ),
        migrations.AddField(
            model_name='executiondistribution',
            name='transaction',
            field=models.OneToOneField(related_name='execution_distribution', to='main.Transaction'),
        ),
        migrations.AddField(
            model_name='execution',
            name='order',
            field=models.ForeignKey(related_name='executions', to='main.MarketOrderRequest'),
        ),
    ]
