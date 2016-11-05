# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ETNALogin',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('ResponseCode', models.PositiveIntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
