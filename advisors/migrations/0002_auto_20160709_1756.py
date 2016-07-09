# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changedealergroup',
            name='work_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128),
        ),
    ]
