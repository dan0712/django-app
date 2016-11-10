# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0070_auto_20161110_0841'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apexorder',
            name='ticker',
        ),
        migrations.DeleteModel(
            name='ApexOrder',
        ),
    ]
