# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20151001_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='prepopulated',
            field=models.BooleanField(default=False),
        ),
    ]
