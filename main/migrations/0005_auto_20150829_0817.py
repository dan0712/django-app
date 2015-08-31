# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20150829_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientinvite',
            name='is_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='clientinvite',
            name='sent_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
