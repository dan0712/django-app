# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0014_auto_20160920_0455'),
    ]

    operations = [
        migrations.CreateModel(
            name='APEXAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('apex_account', models.CharField(max_length=32)),
                ('bs_account', models.OneToOneField(to='client.ClientAccount', related_name='apex_account')),
            ],
        ),
    ]
