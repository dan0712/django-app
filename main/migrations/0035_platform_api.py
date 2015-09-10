# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20150909_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='api',
            field=models.CharField(default='YAHOO', choices=[('YAHOO', 'YAHOO')], max_length=20),
        ),
    ]
