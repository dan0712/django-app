# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_auto_20150916_0247'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='advisor_agreement',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='betasmartz_agreement',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='client',
            name='employment_status',
            field=models.CharField(max_length=20, choices=[('FULL_TIME', 'Employed (full-time)'), ('PART_TIME', 'Employed (part-time)'), ('SELF_EMPLOYED', 'Self-employed'), ('STUDENT', 'Student'), ('RETIRED', 'Retired'), ('HOMEMAKER', 'Homemaker'), ('UNEMPLOYED', 'Not employed')]),
        ),
    ]
