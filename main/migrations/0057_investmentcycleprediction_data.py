# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import csv
import json
import os
from django.conf import settings


def load_cycle_data(apps, schema_editor):
    """
    Expects main/fixtures/predict_probs12.csv to contain
    InvestmentCyclePrediction initial data.

    csv is like Ex:
        as_of_date,pred_date,eq,eq_pk,pk_eq,eq_pit,pit_eq
        31/03/1993,31/03/1994,0.082380986,0.23991326,2.20E-16,0.072761958,0.712514322
    """
    predict_prob_path = os.path.join(settings.BASE_DIR, 'main/fixtures/predict_probs12.csv')
    InvestmentCyclePrediction = apps.get_model('main', 'InvestmentCyclePrediction')
    with open(predict_prob_path) as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            # ignore the head line:  Date, Integer
            if idx != 0:
                # need to do a little data conversion
                # Python wants:  YYYY-MM-DD format csv has DD/MM/YYYY format
                as_of_split = row[0].split('/')
                pred_dt_split = row[1].split('/')
                _, created = InvestmentCyclePrediction.objects.get_or_create(
                    as_of='-'.join([as_of_split[2], as_of_split[1], as_of_split[0]]),
                    pred_dt='-'.join([pred_dt_split[2], pred_dt_split[1], pred_dt_split[0]]),
                    eq=row[2],
                    eq_pk=row[3],
                    pk_eq=row[4],
                    eq_pit=row[5],
                    pit_eq=row[6],
                    source=json.dumps({}),
                )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0056_investmentcycleprediction'),
    ]

    operations = [
        migrations.RunPython(load_cycle_data),
    ]
