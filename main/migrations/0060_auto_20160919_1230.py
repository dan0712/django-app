# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_positionlot_sale'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positionlot',
            name='execution_distribution',
            field=models.OneToOneField(to='main.ExecutionDistribution', related_name='position_lot'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='execution_distribution',
            field=models.OneToOneField(to='main.ExecutionDistribution', related_name='sold_lot'),
        ),
    ]
