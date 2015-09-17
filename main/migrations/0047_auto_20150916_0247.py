# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20150915_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='employer',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='employment_status',
            field=models.CharField(max_length=20, default='UNEMPLOYED', choices=[('FULL_TIME', 'Employed (full-time)'), ('PART_TIME', 'Employed (part-time)'), ('SELF_EMPLOYED', 'SELF_EMPLOYED'), ('STUDENT', 'Student'), ('RETIRED', 'Retired'), ('HOMEMAKER', 'Homemaker'), ('UNEMPLOYED', 'Not employed<')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='income',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='net_worth',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='client',
            name='occupation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='public_position_insider',
            field=models.BooleanField(verbose_name='Do you or a family member hold a public office position.', default=False, choices=[(False, 'No'), (True, 'Yes')]),
        ),
        migrations.AddField(
            model_name='client',
            name='us_citizen',
            field=models.BooleanField(verbose_name='Are you a US citizen/person for the purpose of US Federal Income Tax.', default=False, choices=[(False, 'No'), (True, 'Yes')]),
        ),
    ]
