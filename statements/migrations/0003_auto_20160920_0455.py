# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statements', '0002_retirementstatementofadvice'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordofadvice',
            name='pdf',
            field=models.FileField(upload_to='', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='retirementstatementofadvice',
            name='pdf',
            field=models.FileField(upload_to='', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='statementofadvice',
            name='pdf',
            field=models.FileField(upload_to='', blank=True, null=True),
        ),
    ]
