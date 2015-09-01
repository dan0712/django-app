# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20150901_0542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailinvitation',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
