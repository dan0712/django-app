# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_transaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 9, 9, 2, 45, 2, 86723, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
