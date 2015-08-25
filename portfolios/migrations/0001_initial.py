# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyAssetClass',
            fields=[
            ],
            options={
                'verbose_name': 'Asset class',
                'proxy': True,
                'verbose_name_plural': 'Asset classes',
            },
            bases=('main.assetclass',),
        ),
    ]
