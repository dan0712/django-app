# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0003_retirementplaneinc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementlifestyle',
            name='cost',
            field=models.PositiveIntegerField(help_text="The minimum expected cost in system currency of this lifestyle in today's dollars"),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='atc',
            field=models.PositiveIntegerField(help_text='Annual personal after-tax contributions'),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='btc',
            field=models.PositiveIntegerField(help_text='Annual personal before-tax contributions'),
        ),
    ]
