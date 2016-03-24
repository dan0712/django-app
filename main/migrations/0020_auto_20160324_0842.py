# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


def migrate_archived(apps, schema_editor):
    Goal = apps.get_model("main", "Goal")
    db_alias = schema_editor.connection.alias
    for goal in Goal.objects.using(db_alias).all():
        if goal.archived:
            goal.state = 3
            goal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20160323_0031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='inversion',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='new_balance',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='return_fraction',
        ),
        migrations.AddField(
            model_name='goal',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'ACTIVE'), (1, 'ARCHIVE_REQUESTED'), (2, 'CLOSING'), (3, 'ARCHIVED')]),
        ),
        migrations.RunPython(migrate_archived),
        migrations.RemoveField(
            model_name='goal',
            name='archived',
        ),
        migrations.AddField(
            model_name='goal',
            name='supervised',
            field=models.BooleanField(default=True, help_text='Is this goal supervised by an advisor?'),
        ),
        migrations.AlterField(
            model_name='accountgroup',
            name='advisor',
            field=models.ForeignKey(related_name='primary_account_groups', to='main.Advisor', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='client',
            name='advisor',
            field=models.ForeignKey(related_name='all_clients', to='main.Advisor', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='execution',
            name='asset',
            field=models.ForeignKey(related_name='executions', to='main.Ticker', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='execution',
            name='order',
            field=models.ForeignKey(related_name='executions', to='main.MarketOrderRequest', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='executiondistribution',
            name='execution',
            field=models.ForeignKey(related_name='distributions', to='main.Execution', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='executiondistribution',
            name='transaction',
            field=models.OneToOneField(related_name='execution_distribution', to='main.Transaction', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='executionrequest',
            name='asset',
            field=models.ForeignKey(related_name='execution_requests', to='main.Ticker', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='executionrequest',
            name='goal',
            field=models.ForeignKey(related_name='execution_requests', to='main.Goal', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='executionrequest',
            name='reason',
            field=models.IntegerField(choices=[(0, 'DRIFT'), (1, 'WITHDRAWAL'), (2, 'DEPOSIT'), (3, 'METRIC_CHANGE')]),
        ),
        migrations.AlterField(
            model_name='marketorderrequest',
            name='account',
            field=models.ForeignKey(related_name='market_orders', to='main.ClientAccount', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='marketorderrequest',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'PENDING'), (1, 'APPROVED'), (2, 'SENT'), (3, 'CANCEL_PENDING'), (4, 'COMPLETE')]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='from_goal',
            field=models.ForeignKey(related_name='transactions_from', to='main.Goal', on_delete=django.db.models.deletion.PROTECT, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='to_goal',
            field=models.ForeignKey(related_name='transactions_to', to='main.Goal', on_delete=django.db.models.deletion.PROTECT, blank=True, null=True),
        ),
    ]
