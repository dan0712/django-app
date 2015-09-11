# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_auto_20150911_1955'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomaticDeposit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('frequency', models.CharField(max_length=50, choices=[('MONTHLY', '1/mo'), ('TWICE_A_MONTH', '2/mo'), ('EVERY_OTHER_WEEK', '2/mo'), ('WEEKLY', 'WEEKLY')])),
                ('enabled', models.BooleanField(default=True)),
                ('amount', models.FloatField()),
                ('transaction_date_time_1', models.DateTimeField(null=True)),
                ('transaction_date_time_2', models.DateTimeField(null=True)),
                ('last_plan_change', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.OneToOneField(to='main.Goal', related_name='auto_deposit')),
            ],
        ),
    ]
