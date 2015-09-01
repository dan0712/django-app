# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150901_1452'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='firmdata',
            options={'verbose_name': 'Firm details'},
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='investor_transfer',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='previous_adviser_name',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='previous_bt_adviser_number',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='previous_margin_lending_adviser_number',
        ),
        migrations.AddField(
            model_name='firmdata',
            name='firm',
            field=models.OneToOneField(to='main.Firm', default=1, related_name='firm_details'),
            preserve_default=False,
        ),
    ]
