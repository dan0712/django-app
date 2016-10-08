# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0014_auto_20160920_0455'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='emailinvite',
            unique_together=set([('advisor', 'email')]),
        ),
    ]
