# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150901_1451'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='address_line_2',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='AuthorisedRepresentative',
            name='address_line_2',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
