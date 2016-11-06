# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0011_auto_20161104_0253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementadvice',
            name='trigger',
            field=models.ForeignKey(related_name='advice', to='eventlog.Log', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='initial_deposits',
            field=jsonfield.fields.JSONField(null=True, blank=True, help_text='List of deposits [{id, asset, goal, amt},...]'),
        ),
    ]
