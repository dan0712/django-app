# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_goal'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientaccount',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 4, 10, 57, 57, 210696, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='advisor',
            name='firm',
            field=models.ForeignKey(to='main.Firm', related_name='advisors'),
        ),
    ]
