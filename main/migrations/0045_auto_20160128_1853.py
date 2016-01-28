# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_markowitzscale'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='position',
            unique_together=set([('goal', 'ticker')]),
        ),
    ]
