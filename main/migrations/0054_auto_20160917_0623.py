# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_auto_20160913_1404'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='retirementplan',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='retirementplan',
            name='client',
        ),
        migrations.RemoveField(
            model_name='retirementplan',
            name='partner_plan',
        ),
        migrations.RemoveField(
            model_name='retirementplan',
            name='smsf_account',
        ),
        migrations.RemoveField(
            model_name='retirementplanatc',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='retirementplanbtc',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='retirementplaneinc',
            name='plan',
        ),
        migrations.DeleteModel(
            name='RetirementPlan',
        ),
        migrations.DeleteModel(
            name='RetirementPlanATC',
        ),
        migrations.DeleteModel(
            name='RetirementPlanBTC',
        ),
        migrations.DeleteModel(
            name='RetirementPlanEinc',
        ),
    ]
