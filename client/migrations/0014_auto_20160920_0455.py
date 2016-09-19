# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0013_riskcategory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='riskcategory',
            name='name',
        ),
        migrations.AlterField(
            model_name='client',
            name='height',
            field=models.PositiveIntegerField(blank=True, null=True, help_text='In centimeters'),
        ),
        migrations.AlterField(
            model_name='client',
            name='weight',
            field=models.PositiveIntegerField(blank=True, null=True, help_text='In kilograms'),
        ),
    ]
