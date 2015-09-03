# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20150903_0337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='advisor',
            field=models.ForeignKey(related_name='clients', to='main.Advisor'),
        ),
        migrations.AlterField(
            model_name='client',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
