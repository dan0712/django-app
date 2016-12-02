# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0078_auto_20161202_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(null=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(null=True, max_length=30),
        ),
    ]
