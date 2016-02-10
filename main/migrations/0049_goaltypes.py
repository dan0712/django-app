# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_delete_goaltypes'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('default_term', models.IntegerField()),
                ('code', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'db_table': 'goal_types',
            },
        ),
    ]
