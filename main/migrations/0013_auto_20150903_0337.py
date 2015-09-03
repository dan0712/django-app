# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20150902_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='client_agreement',
            field=models.FileField(upload_to='', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='create_date',
            field=models.DateField(auto_now_add=True, default=datetime.datetime(2015, 9, 3, 3, 37, 21, 202097, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
