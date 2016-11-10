# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0068_orderetna'),
    ]

    operations = [
        migrations.AddField(
            model_name='apexfill',
            name='etna_order',
            field=models.ForeignKey(related_name='etna_fills', default=None, to='main.OrderETNA'),
        ),
        migrations.AddField(
            model_name='marketorderrequestapex',
            name='etna_order',
            field=models.ForeignKey(related_name='morsAPEX', default=None, to='main.OrderETNA'),
        ),
    ]
