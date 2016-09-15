# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_auto_20160913_1404'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentCycleObservation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('as_of', models.DateField()),
                ('recorded', models.DateField()),
                ('cycle', models.IntegerField(choices=[(0, 'eq'), (1, 'eq_pk'), (2, 'pk_eq'), (3, 'eq_pit'), (4, 'pit_eq')])),
                ('source', jsonfield.fields.JSONField()),
            ],
        ),
    ]
