# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F
from django.utils.timezone import utc
import datetime

def set_dates(apps, schema_editor):
    Country = apps.get_model("main", "RecurringTransaction")
    db_alias = schema_editor.connection.alias
    Country.objects.using(db_alias).all().update(begin_date=F('created_at'),
                                                 modified_at=F('created_at'))

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_auto_20160804_0626'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recurringtransaction',
            old_name='recurrence',
            new_name='schedule'
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='begin_date',
            field=models.DateField(default=datetime.datetime(2016, 1, 1, 1, 1, 1, 0, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='growth',
            field=models.FloatField(help_text='Annualized rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change', default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recurringtransaction',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 1, 1, 1, 1, 1, 0, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='externalassettransfer',
            name='schedule',
            field=models.TextField(help_text='RRULE to specify when the transfer happens'),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='amount',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='retirementplanatc',
            name='schedule',
            field=models.TextField(help_text='RRULE to specify when the transfer happens'),
        ),
        migrations.AlterField(
            model_name='retirementplanbtc',
            name='schedule',
            field=models.TextField(help_text='RRULE to specify when the transfer happens'),
        ),
        migrations.AlterField(
            model_name='retirementplaneinc',
            name='schedule',
            field=models.TextField(help_text='RRULE to specify when the transfer happens'),
        ),
        migrations.RunPython(set_dates)
    ]
