# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20160310_0058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticker',
            name='benchmark_content_type',
            field=models.ForeignKey(verbose_name='Benchmark Type', null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='benchmark_object_id',
            field=models.PositiveIntegerField(verbose_name='Benchmark Instrument', null=True),
        ),
    ]
