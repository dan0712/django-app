# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150901_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='medicare_number',
        ),
        migrations.AddField(
            model_name='advisor',
            name='medicare_number',
            field=models.CharField(max_length=50, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='legalrepresentative',
            name='medicare_number',
            field=models.CharField(max_length=50, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='legalrepresentative',
            name='betasmartz_agreement',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='legalrepresentative',
            name='user',
            field=models.OneToOneField(related_name='legal_representative', to=settings.AUTH_USER_MODEL),
        ),
    ]
