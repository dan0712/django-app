# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0015_auto_20160930_0010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailinvite',
            old_name='onboarding_file_1',
            new_name='tax_transcript',
        ),
        migrations.AlterUniqueTogether(
            name='emailinvite',
            unique_together=set([('advisor', 'email')]),
        ),
    ]
