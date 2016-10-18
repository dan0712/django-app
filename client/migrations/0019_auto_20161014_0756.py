# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0018_riskcategory_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailinvite',
            name='middle_name',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
