# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retirementplan',
            name='income',
            field=models.PositiveIntegerField(help_text='The current annual personal pre-tax income at the start of your plan'),
        ),
    ]
