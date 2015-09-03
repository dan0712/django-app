# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20150903_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='secondary_advisors',
            field=models.ManyToManyField(related_name='secondary_clients', to='main.Advisor', editable=False),
        ),
        migrations.AlterField(
            model_name='emailinvitation',
            name='invitation_type',
            field=models.PositiveIntegerField(choices=[(0, 'Advisor'), (1, 'Authorised representative'), (3, 'Client'), (2, 'Supervisor')], default=3),
        ),
    ]
