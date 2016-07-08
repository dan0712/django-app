# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='global_id',
            field=models.CharField(help_text='Global identifier of the address in whatever API we are using (if any)', null=True, max_length=64, blank=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('country', 'code'), ('country', 'name')]),
        ),
    ]
