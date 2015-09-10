# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_platform_api'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='currency',
            field=models.CharField(max_length=10, default='AUD'),
        ),
    ]
