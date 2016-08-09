# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0002_auto_20160709_1756'),
        ('client', '0001_initial'),
    ]

    state_operations = [
        migrations.AlterField(
            model_name='bulkinvestortransfer',
            name='investors',
            field=models.ManyToManyField(to='client.Client'),
        ),
        migrations.AlterField(
            model_name='singleinvestortransfer',
            name='investor',
            field=models.ForeignKey(to='client.Client'),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations
        )
    ]
