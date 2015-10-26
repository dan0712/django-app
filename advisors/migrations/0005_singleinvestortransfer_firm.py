# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20151022_1509'),
        ('advisors', '0004_auto_20151025_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='singleinvestortransfer',
            name='firm',
            field=models.ForeignKey(default=1, to='main.Firm', editable=False),
            preserve_default=False,
        ),
    ]
