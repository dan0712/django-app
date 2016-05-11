# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def default_activity_log_events(apps, schema_editor):
    ActivityLog = apps.get_model("main", "ActivityLog")
    ActivityLogEvent = apps.get_model("main", "ActivityLogEvent")
    db_alias = schema_editor.connection.alias
    alog = ActivityLog.objects.using(db_alias).create(name='Dividend Transaction',
                                               format_str='Dividend payment of {} AUD into goal',
                                               format_args='transaction.amount')
    ActivityLogEvent.objects.using(db_alias).create(id=14, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Goal Deposit Transaction',
                                              format_str='Deposit of {} AUD from Account to Goal',
                                              format_args='transaction.amount')
    ActivityLogEvent.objects.using(db_alias).create(id=13, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Goal Withdrawal Transaction',
                                              format_str='Withdrawal of {} AUD from Goal to Account',
                                              format_args='transaction.amount')
    ActivityLogEvent.objects.using(db_alias).create(id=12, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Goal Rebalance Transaction', format_str='Rebalance Applied')
    ActivityLogEvent.objects.using(db_alias).create(id=16, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Goal Transfer Transaction', format_str='Transfer Applied')
    ActivityLogEvent.objects.using(db_alias).create(id=17, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Goal Fee Transaction',
                                              format_str='Fee of {} AUD applied',
                                              format_args='transaction.amount')
    ActivityLogEvent.objects.using(db_alias).create(id=15, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Order Distribution Transaction', format_str='Order Distributed')
    ActivityLogEvent.objects.using(db_alias).create(id=18, activity_log=alog)
    alog = ActivityLog.objects.using(db_alias).create(name='Daily Balance', format_str='Daily Balance')
    ActivityLogEvent.objects.using(db_alias).create(id=11, activity_log=alog)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20160508_2048'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('format_str', models.TextField()),
                ('format_args', models.TextField(null=True, help_text="Dotted '.' dictionary path into the event 'extra' field for each arg in the format_str. Each arg path separated by newline.Eg. 'request.amount'", blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLogEvent',
            fields=[
                ('id', models.IntegerField(primary_key=True, choices=[(0, 'PLACE_MARKET_ORDER'), (1, 'CANCEL_MARKET_ORDER'), (2, 'ARCHIVE_GOAL_REQUESTED'), (3, 'ARCHIVE_GOAL'), (4, 'REACTIVATE_GOAL'), (5, 'APPROVE_SELECTED_SETTINGS'), (6, 'REVERT_SELECTED_SETTINGS'), (7, 'SET_SELECTED_SETTINGS'), (8, 'UPDATE_SELECTED_SETTINGS'), (9, 'GOAL_WITHDRAWAL'), (10, 'GOAL_DEPOSIT'), (11, 'GOAL_BALANCE_CALCULATED'), (12, 'GOAL_WITHDRAWAL_EXECUTED'), (13, 'GOAL_DEPOSIT_EXECUTED'), (14, 'GOAL_DIVIDEND_DISTRIBUTION'), (15, 'GOAL_FEE_LEVIED'), (16, 'GOAL_REBALANCE_EXECUTED'), (17, 'GOAL_TRANSFER_EXECUTED'), (18, 'GOAL_ORDER_DISTRIBUTION')], serialize=False)),
                ('activity_log', models.ForeignKey(to='main.ActivityLog', related_name='events')),
            ],
        ),
        migrations.RunPython(default_activity_log_events),
        migrations.DeleteModel(
            name='DataApiDict',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='executed',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
