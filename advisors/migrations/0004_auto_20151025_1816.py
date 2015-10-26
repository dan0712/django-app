# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0003_auto_20151025_1248'),
    ]

    operations = [
        migrations.RenameField(
            model_name='singleinvestortransfer',
            old_name='signature_advisor',
            new_name='signatures',
        ),
        migrations.RemoveField(
            model_name='singleinvestortransfer',
            name='signature_investor',
        ),
        migrations.RemoveField(
            model_name='singleinvestortransfer',
            name='signature_joint_investor',
        ),
    ]
