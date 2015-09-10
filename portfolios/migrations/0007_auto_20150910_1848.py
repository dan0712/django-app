# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0006_view'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='view',
            name='assets',
        ),
        migrations.AddField(
            model_name='view',
            name='assets',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
