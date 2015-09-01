# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150831_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firm',
            name='dealer_group_number',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='firm',
            name='knocked_out_logo_url',
            field=models.ImageField(blank=True, verbose_name='Colored logo', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='firm',
            name='logo_url',
            field=models.ImageField(blank=True, verbose_name='White logo', null=True, upload_to=''),
        ),
    ]
