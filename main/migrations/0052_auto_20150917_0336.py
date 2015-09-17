# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20150917_0323'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SymbolHistory',
            new_name='SymbolReturnHistory',
        ),
        migrations.RenameField(
            model_name='symbolreturnhistory',
            old_name='price',
            new_name='return_number',
        ),
        migrations.AlterField(
            model_name='performer',
            name='symbol',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
