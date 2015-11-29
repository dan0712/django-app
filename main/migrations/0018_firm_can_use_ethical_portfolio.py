# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20151129_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='firm',
            name='can_use_ethical_portfolio',
            field=models.BooleanField(default=True),
        ),
    ]
