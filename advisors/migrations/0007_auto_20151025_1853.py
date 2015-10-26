# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0006_auto_20151025_1845'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bulkinvestortransfer',
            old_name='bulk_investors_spreadsheet',
            new_name='investors',
        ),
    ]
