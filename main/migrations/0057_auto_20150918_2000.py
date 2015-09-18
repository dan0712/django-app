# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0056_dataapidict'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataapidict',
            name='api',
            field=models.CharField(max_length=50, choices=[('YAHOO', 'YAHOO'), ('GOOGLE', 'GOOGLE')]),
        ),
        migrations.AlterField(
            model_name='platform',
            name='api',
            field=models.CharField(max_length=20, default='YAHOO', choices=[('YAHOO', 'YAHOO'), ('GOOGLE', 'GOOGLE')]),
        ),
    ]
