# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0066_auto_20150920_0357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialplan',
            name='client',
            field=models.OneToOneField(related_name='financial_plan', to='main.Client'),
        ),
    ]
