# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_auto_20150917_0917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='net_change',
        ),
    ]
