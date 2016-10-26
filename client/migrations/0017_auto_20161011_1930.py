# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0016_auto_20161009_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='other_income',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='signatories',
            field=models.ManyToManyField(to='client.Client', blank=True, related_name='signatory_accounts', help_text='Other clients authorised to operate the account.'),
        ),
    ]
