# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0021_auto_20161019_0226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riskprofilegroup',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
