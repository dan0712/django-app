# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20151014_0839'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientaccount',
            name='account_class',
            field=models.CharField(choices=[('joint_account', 'Joint Account'), ('trust_account', 'SMSF/Trust Account')], max_length=20, default='trust_account'),
        ),
    ]
