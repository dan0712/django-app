# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0020_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='riskcategory',
            options={'verbose_name_plural': 'Risk Categories', 'verbose_name': 'Risk Category', 'ordering': ['upper_bound']},
        ),
    ]
