# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0014_auto_20151108_0714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='city',
            field=models.CharField(verbose_name='City/Town', default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='city',
            field=models.CharField(verbose_name='City/Town', default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='client',
            name='city',
            field=models.CharField(verbose_name='City/Town', default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='middle_name',
            field=models.CharField(verbose_name='middle name (s)', blank=True, max_length=30),
        ),
    ]
