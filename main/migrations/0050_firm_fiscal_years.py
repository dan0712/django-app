# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0049_auto_20160831_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='firm',
            name='fiscal_years',
            field=models.ManyToManyField(to='main.FiscalYear'),
        ),
    ]
