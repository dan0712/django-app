# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20151230_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisor',
            name='last_action',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 1, 7, 11, 14, 1, 770289, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='last_action',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 1, 7, 11, 14, 9, 762743, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
