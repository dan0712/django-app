# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150901_0111'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailinvitation',
            old_name='object_id',
            new_name='inviter_id',
        ),
        migrations.RenameField(
            model_name='emailinvitation',
            old_name='content_type',
            new_name='inviter_type',
        ),
        migrations.AlterField(
            model_name='firm',
            name='slug',
            field=models.CharField(editable=False, max_length=100, unique=True),
        ),
    ]
