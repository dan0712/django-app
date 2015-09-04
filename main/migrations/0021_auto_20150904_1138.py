# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20150904_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='firm',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='user',
        ),
        migrations.DeleteModel(
            name='AuthorisedRepresentative',
        ),
    ]
