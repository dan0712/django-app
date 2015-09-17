# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_performer_symbolhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performer',
            name='symbol',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
