# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_auto_20160818_2344'),
    ]

    operations = [
        migrations.RunSQL('''
    UPDATE main_recurringtransaction SET begin_date = date(created_at)
        ''')
    ]
