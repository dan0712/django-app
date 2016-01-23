# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20160123_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='last_action',
            field=models.DateTimeField(null=True),
        ),
    ]
