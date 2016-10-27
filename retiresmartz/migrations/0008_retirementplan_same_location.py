# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0007_auto_20161027_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='retirementplan',
            name='same_location',
            field=models.NullBooleanField(help_text='Will you be retiring in the same general location?'),
        ),
    ]
