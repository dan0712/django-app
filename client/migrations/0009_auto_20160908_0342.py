# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0008_auto_20160908_0327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientaccount',
            name='risk_profile_group',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='risk_profile_responses',
        ),
    ]
