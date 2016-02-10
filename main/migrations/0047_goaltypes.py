# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20160201_0927'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('default_term', models.IntegerField()),
                ('code', models.CharField(unique=True, max_length=255)),
            ],
        ),
    ]
