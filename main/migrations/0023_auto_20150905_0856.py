# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_authorisedrepresentative'),
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('fee', models.PositiveIntegerField(max_length=3)),
            ],
        ),
        migrations.AlterField(
            model_name='clientaccount',
            name='custom_fee',
            field=models.PositiveIntegerField(default=0, max_length=3),
        ),
    ]
