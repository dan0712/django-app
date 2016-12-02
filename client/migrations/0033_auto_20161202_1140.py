# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0032_auto_20161202_0202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='civil_status',
            field=models.IntegerField(choices=[(0, 'Single'), (1, 'Married Filing Jointly'), (2, 'Married Filing Separately (lived with spouse)'), (3, "Married Filing Separately (didn't live with spouse)"), (4, 'Head of Household'), (5, 'Qualifying Widow(er)')], null=True),
        ),
    ]
