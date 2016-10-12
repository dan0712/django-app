# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0017_auto_20161011_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskcategory',
            name='name',
            field=models.CharField(default='blah', unique=True, max_length=64),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='riskcategory',
            options={'ordering': ['upper_bound']},
        ),
    ]
