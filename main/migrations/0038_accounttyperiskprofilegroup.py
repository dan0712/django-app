# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20160624_0003'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountTypeRiskProfileGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('account_type', models.IntegerField(unique=True, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account')])),
                ('risk_profile_group', models.ForeignKey(related_name='account_types', to='main.RiskProfileGroup')),
            ],
        ),
    ]
