# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0065_auto_20150920_0013'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialplan',
            name='accounts',
            field=models.TextField(default='[]'),
        ),
        migrations.AddField(
            model_name='financialplan',
            name='desired_retirement_income_cents',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='financialplan',
            name='retirement_age',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='financialplan',
            name='savings_advice_chance',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='financialplan',
            name='spouse_retirement_age',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
