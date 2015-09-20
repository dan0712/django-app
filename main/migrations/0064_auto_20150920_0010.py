# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_auto_20150919_2324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialplan',
            name='client',
            field=models.ForeignKey(related_name='financial_plans', to='main.Client'),
        ),
        migrations.AlterField(
            model_name='financialprofile',
            name='client',
            field=models.OneToOneField(related_name='financial_profile', to='main.Client'),
        ),
    ]
