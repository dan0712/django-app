# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_investmentcycleobservation_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentCyclePrediction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('as_of', models.DateField()),
                ('pred_dt', models.DateField()),
                ('eq', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('eq_pk', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('pk_eq', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('eq_pit', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('pit_eq', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('source', jsonfield.fields.JSONField()),
            ],
        ),
    ]
