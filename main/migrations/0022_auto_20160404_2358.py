# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20160404_2002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goal',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='goal',
            name='order',
            field=models.IntegerField(default=0, help_text='The desired position in the list of Goals'),
        ),
    ]
