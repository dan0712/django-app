# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_auto_20150905_0950'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('type', models.CharField(max_length=20, choices=[('DEPOSIT', 'DEPOSIT')])),
                ('amount', models.BigIntegerField(default=0)),
                ('account', models.ForeignKey(to='main.ClientAccount', related_name='transactions')),
                ('from_account', models.ForeignKey(null=True, related_name='transactions_from', to='main.ClientAccount', blank=True)),
                ('to_account', models.ForeignKey(null=True, related_name='transactions_to', to='main.ClientAccount', blank=True)),
            ],
        ),
    ]
