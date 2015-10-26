# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0002_auto_20150927_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='changedealergroup',
            name='new_email',
            field=models.EmailField(max_length=254, default='example@example.com'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='changedealergroup',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
