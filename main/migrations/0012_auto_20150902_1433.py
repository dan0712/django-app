# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_firmdata_same_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisor',
            name='betasmartz_agreement',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='letter_of_authority',
            field=models.FileField(upload_to='', default=''),
            preserve_default=False,
        ),
    ]
