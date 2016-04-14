# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20160413_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jointaccount',
            name='client',
        ),
        migrations.RemoveField(
            model_name='jointaccount',
            name='joined',
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='signatories',
            field=models.ManyToManyField(to='main.Client', help_text='Other clients authorised to operate the account.', related_name='signatory_accounts'),
        ),
        migrations.DeleteModel(
            name='JointAccount',
        ),
    ]
