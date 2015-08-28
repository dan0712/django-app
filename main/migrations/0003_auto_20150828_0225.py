# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150827_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='confirmation_key',
            field=models.CharField(null=True, max_length=36),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='advisor'),
        ),
    ]
