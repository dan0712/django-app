# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20150901_2022'),
    ]

    operations = [
        migrations.AddField(
            model_name='firmdata',
            name='same_address',
            field=models.BooleanField(default=False),
        ),
    ]
