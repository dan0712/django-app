# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_set_recurringtransaction_begin_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='firm',
            old_name='form_adv_part2_url',
            new_name='form_adv_part2',
        ),
        migrations.RenameField(
            model_name='firm',
            old_name='knocked_out_logo_url',
            new_name='knocked_out_logo',
        ),
        migrations.RenameField(
            model_name='firm',
            old_name='logo_url',
            new_name='logo',
        ),
    ]
