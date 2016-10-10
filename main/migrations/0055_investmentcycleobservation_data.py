# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import csv
from datetime import datetime
import json
import os
from django.conf import settings


def load_cycle_data(apps, schema_editor):
    """
    Expects main/fixtures/CycleVar.csv to contain
    InvestmentCycleObservation initial data.

    csv is like Ex:
        Date, Integer
        30/11/1992,5
    """
    cycle_var_path = os.path.join(settings.BASE_DIR, 'main/fixtures/CycleVar.csv')
    InvestmentCycleObservation = apps.get_model('main', 'InvestmentCycleObservation')
    with open(cycle_var_path) as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            # ignore the head line:  Date, Integer
            if idx != 0:
                # need to do a little data conversion
                # Python wants:  YYYY-MM-DD format csv has DD/MM/YYYY format
                as_of_split = row[0].split('/')
                _, created = InvestmentCycleObservation.objects.get_or_create(
                    as_of='-'.join([as_of_split[2], as_of_split[1], as_of_split[0]]),
                    recorded=datetime(year=2016, day=15, month=9),
                    cycle=int(row[1])-1, # We use 0 for the eq phase of the cycle
                    source=json.dumps({}),
                )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_investmentcycleobservation'),
    ]

    operations = [
        migrations.RunPython(load_cycle_data),
    ]
