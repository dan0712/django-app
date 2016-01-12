# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_supervisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='supervisor',
            name='firm',
            field=models.ForeignKey(to='main.Firm', default=1, related_name='FirmSupervisors'),
            preserve_default=False,
        ),
    ]
