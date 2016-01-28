# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0043_auto_20160125_2144'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarkowitzScale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('min', models.FloatField()),
                ('max', models.FloatField()),
            ],
        ),
    ]
