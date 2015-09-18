# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_goal_income'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomaticWithdrawal',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('frequency', models.CharField(choices=[('MONTHLY', '1/mo'), ('TWICE_A_MONTH', '2/mo'), ('EVERY_OTHER_WEEK', '2/mo'), ('WEEKLY', 'WEEKLY')], max_length=50)),
                ('enabled', models.BooleanField(default=True)),
                ('amount', models.FloatField()),
                ('transaction_date_time_1', models.DateTimeField(null=True)),
                ('transaction_date_time_2', models.DateTimeField(null=True)),
                ('last_plan_change', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('account', models.OneToOneField(to='main.Goal', related_name='auto_withdrawal')),
            ],
        ),
    ]
