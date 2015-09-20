# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0069_auto_20150920_0656'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialplanaccount',
            name='client',
            field=models.ForeignKey(default=1, to='main.Client'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='financialplanexternalaccount',
            name='client',
            field=models.ForeignKey(default=1, to='main.Client'),
            preserve_default=False,
        ),
    ]
