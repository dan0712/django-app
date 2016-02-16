# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_goaltypes'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='goal',
            name='duration',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='goal',
            name='ethical_investments',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='goal',
            name='initialDeposit',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='goaltypes',
            name='group',
            field=models.CharField(null=True, max_length=255),
        ),
    ]
