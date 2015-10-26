# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20151026_0635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientaccount',
            name='account_type',
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='account_name',
            field=models.CharField(default='PERSONAL', max_length=255),
        ),
    ]
