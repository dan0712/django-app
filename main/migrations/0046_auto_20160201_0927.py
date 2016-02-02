# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_auto_20160128_1853'),
    ]

    operations = [
        migrations.AddField(
            model_name='markowitzscale',
            name='a',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='markowitzscale',
            name='b',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='markowitzscale',
            name='c',
            field=models.FloatField(null=True),
        ),
    ]
