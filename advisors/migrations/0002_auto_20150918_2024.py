# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='singleinvestortransfer',
            old_name='investors',
            new_name='investor',
        ),
    ]
