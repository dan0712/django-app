# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0002_auto_20160920_0455'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetirementPlanEinc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField(help_text='RRULE to specify when the transfer happens')),
                ('name', models.CharField(max_length=128)),
                ('plan', models.ForeignKey(related_name='external_income', to='retiresmartz.RetirementPlan')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
