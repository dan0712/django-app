# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JointAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('client', models.ForeignKey(to='main.Client', related_name='joint_accounts')),
            ],
        ),
        migrations.CreateModel(
            name='RecurringTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('recurrence', recurrence.fields.RecurrenceField()),
                ('enabled', models.BooleanField(default=True)),
                ('amount', models.FloatField()),
                ('last_plan_change', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='AutomaticWithdrawal',
        ),
        migrations.RemoveField(
            model_name='goalmetric',
            name='goal',
        ),
        migrations.RemoveField(
            model_name='goalsetting',
            name='auto_deposit',
        ),
        migrations.AddField(
            model_name='goalmetric',
            name='setting',
            field=models.ForeignKey(to='main.GoalSetting', null=True, related_name='metrics'),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='primary_owner',
            field=models.ForeignKey(to='main.Client', related_name='primary_accounts'),
        ),
        migrations.DeleteModel(
            name='AutomaticDeposit',
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='setting',
            field=models.ForeignKey(to='main.GoalSetting', null=True, related_name='recurring_transactions'),
        ),
        migrations.AddField(
            model_name='jointaccount',
            name='joined',
            field=models.ForeignKey(to='main.ClientAccount', related_name='joint_holder'),
        ),
    ]
