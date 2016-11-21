# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apexorder',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, 'PENDING'), (1, 'APPROVED'), (2, 'SENT'), (3, 'CANCEL_PENDING'), (4, 'COMPLETE'), (5, 'ARCHIVED')]),
        ),
    ]
