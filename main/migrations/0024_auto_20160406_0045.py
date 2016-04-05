# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20160405_1917'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goaltype',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='goaltype',
            name='order',
            field=models.IntegerField(default=0, help_text='The order of the type in the list.'),
        ),
    ]
