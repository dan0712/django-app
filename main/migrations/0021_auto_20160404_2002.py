# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20160324_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='employment_status',
            field=models.IntegerField(null=True, choices=[(0, 'Employed (full-time)'), (1, 'Employed (part-time)'), (2, 'Self-employed'), (3, 'Student'), (4, 'Retired'), (5, 'Homemaker'), (6, 'Not employed')]),
        ),
    ]
