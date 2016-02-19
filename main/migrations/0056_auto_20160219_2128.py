# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_auto_20160219_2113'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='employment_status_int',
            new_name='employment_status',
        ),
        migrations.AlterField(
            model_name='client',
            name='employment_status',
            field=models.IntegerField(choices=[(0, 'Employed (full-time)'), (1, 'Employed (part-time)'), (1, 'Self-employed'), (2, 'Student'), (3, 'Retired'), (4, 'Homemaker'), (5, 'Not employed')]),
        ),
    ]
