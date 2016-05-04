# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20160430_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='goaltype',
            name='risk_factor_weights',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
