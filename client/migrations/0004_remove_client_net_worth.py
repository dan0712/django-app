# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_emailinvite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='net_worth',
        ),
    ]
