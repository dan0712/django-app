# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import client.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('client', '0006_auto_20160906_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailinvite',
            name='invite_key',
            field=models.CharField(max_length=64, default=client.models.generate_token),
        ),
        migrations.AddField(
            model_name='emailinvite',
            name='onboarding_data',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emailinvite',
            name='onboarding_file_1',
            field=models.FileField(upload_to='', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emailinvite',
            name='user',
            field=models.OneToOneField(related_name='invitation', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='emailinvite',
            name='status',
            field=models.PositiveIntegerField(choices=[(0, 'Created'), (1, 'Sent'), (2, 'Accepted'), (3, 'Expired'), (4, 'Complete')], default=0),
        ),
    ]
