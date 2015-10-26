# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20151022_1509'),
        ('advisors', '0005_singleinvestortransfer_firm'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bulkinvestortransfer',
            old_name='signature',
            new_name='signatures',
        ),
        migrations.AddField(
            model_name='bulkinvestortransfer',
            name='firm',
            field=models.ForeignKey(to='main.Firm', editable=False, default=1),
            preserve_default=False,
        ),
    ]
