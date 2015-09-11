# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20150910_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='change_allocation',
            field=models.BooleanField(editable=False, default=True),
        ),
    ]
