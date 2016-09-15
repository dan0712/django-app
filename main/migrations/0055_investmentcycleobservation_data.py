# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import csv
from datetime import datetime
import json


def load_cycle_data(apps, schema_editor):
    """
    Expects main/fixtures/CycleVar.csv to contain
    InvestmentCycleObservation initial data.

    csv is like Ex:
        Date, Integer
        30/11/1992,5
    """
    cycle_var_path = 'main/fixtures/CycleVar.csv'
    InvestmentCycleObservation = apps.get_model('main', 'InvestmentCycleObservation')
    with open(cycle_var_path) as f:
        reader = csv.reader(f)
        for row in reader:
            _, created = InvestmentCycleObservation.objects.get_or_create(
                as_of=row[0],
                recorded=datetime(year=2016, day=15, month=9),
                cycle=row[1],
                source=json.dumps({}),
            )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_investmentcycleobservation'),
    ]

    operations = [
        migrations.RunPython(load_cycle_data),
    ]
