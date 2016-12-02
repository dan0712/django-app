# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0033_auto_20161202_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(null=True, max_length=30),
        ),
    ]
