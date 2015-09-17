# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_auto_20150917_0336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbolreturnhistory',
            name='return_number',
            field=models.FloatField(default=0),
        ),
    ]
