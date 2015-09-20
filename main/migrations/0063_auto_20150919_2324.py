# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0062_financialplan_financialprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialprofile',
            name='spouse_estimated_birthdate',
            field=models.DateTimeField(null=True),
        ),
    ]
