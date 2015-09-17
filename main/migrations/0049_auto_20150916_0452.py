# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_auto_20150916_0428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='tax_file_number',
            field=models.CharField(null=True, max_length=50, blank=True),
        ),
    ]
