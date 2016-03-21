# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20160318_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='goaltypes',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterModelTable(
            name='goaltypes',
            table=None,
        ),
        migrations.RenameModel('GoalTypes', 'GoalType'),
    ]
