# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20160408_1933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='supervised',
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='supervised',
            field=models.BooleanField(default=True, help_text='Is this account supervised by an advisor?'),
        ),
    ]
