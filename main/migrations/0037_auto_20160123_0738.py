# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20160123_0426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='account',
            field=models.ForeignKey(related_name='transactions', to='main.Goal', null=True),
        ),
    ]
