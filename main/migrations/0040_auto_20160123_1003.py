# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_auto_20160123_0744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='share',
            field=models.FloatField(default=0),
        ),
    ]
