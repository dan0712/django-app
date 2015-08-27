# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='advisor',
            old_name='accepted',
            new_name='is_accepted',
        ),
        migrations.AddField(
            model_name='advisor',
            name='is_supervisor',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='work_phone',
            field=django_localflavor_au.models.AUPhoneNumberField(max_length=10),
        ),
    ]
