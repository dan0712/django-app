# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0055_remove_transaction_net_change'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataApiDict',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('api', models.CharField(max_length=50, choices=[('YAHOO', 'YAHOO')])),
                ('platform_symbol', models.CharField(max_length=20)),
                ('api_symbol', models.CharField(max_length=20)),
            ],
        ),
    ]
