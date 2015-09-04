# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20150904_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientaccount',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
