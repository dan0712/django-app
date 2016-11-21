# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0013_auto_20161109_0520'),
    ]

    operations = [
        migrations.AddField(
            model_name='retirementplan',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 9, 20, 12, 19, 540680, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 11, 9, 20, 12, 29, 945963, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
