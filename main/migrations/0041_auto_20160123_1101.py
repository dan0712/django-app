# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0040_auto_20160123_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='goal',
            name='account',
            field=models.ForeignKey(related_name='__all_goals', to='main.ClientAccount'),
        ),
    ]
