# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_set_recurringtransaction_begin_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalassettransfer',
            name='growth',
            field=models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change'),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='growth',
            field=models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change'),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='schedule',
            field=models.TextField(help_text='RRULE to specify when the transfer happens'),
        ),
        migrations.AlterField(
            model_name='retirementplanatc',
            name='growth',
            field=models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change'),
        ),
        migrations.AlterField(
            model_name='retirementplanbtc',
            name='growth',
            field=models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change'),
        ),
        migrations.AlterField(
            model_name='retirementplaneinc',
            name='growth',
            field=models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change'),
        ),
    ]
