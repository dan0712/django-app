# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
import re
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0012_auto_20151027_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='associated_to_broker_dealer',
            field=models.BooleanField(choices=[(False, 'No'), (True, 'Yes')],
                                      verbose_name='Are employed by or associated with a broker dealer?',
                                      default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='income',
            field=models.FloatField(verbose_name='Income ($)', default=0),
        ),
        migrations.AlterField(
            model_name='client',
            name='net_worth',
            field=models.FloatField(verbose_name='Net worth ($)', default=0),
        ),
        migrations.AlterField(
            model_name='client',
            name='public_position_insider',
            field=models.BooleanField(choices=[(False, 'No'), (True, 'Yes')],
                                      verbose_name='Do you or a family member hold a public office position?',
                                      default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='tax_file_number',
            field=models.CharField(blank=True, validators=[
                django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid',
                                                      message='Enter a valid number.'),
                django.core.validators.MaxLengthValidator(limit_value=9)], null=True, max_length=9),
        ),
        migrations.AlterField(
            model_name='client',
            name='ten_percent_insider',
            field=models.BooleanField(choices=[(False, 'No'), (True, 'Yes')],
                                      verbose_name='Are you a 10% shareholder, director, or policy maker of a publicly traded company?',
                                      default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='us_citizen',
            field=models.BooleanField(choices=[(False, 'No'), (True, 'Yes')],
                                      verbose_name='Are you a US citizen/person for the purpose of US Federal Income Tax?',
                                      default=False),
        ),
    ]
