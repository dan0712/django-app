# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_supervisor_firm'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientaccount',
            name='tax_loss_harvesting_consent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='tax_loss_harvesting_status',
            field=models.CharField(max_length=255, default='USER_OFF', choices=[('USER_OFF', 'USER_OFF'), ('USER_ON', 'USER_ON')]),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='can_write',
            field=models.BooleanField(verbose_name='Has Full Access?', default=False, help_text="A supervisor with 'full access' can impersonate advisors and clients and make any action as them."),
        ),
        migrations.AlterField(
            model_name='supervisor',
            name='firm',
            field=models.ForeignKey(related_name='supervisors', to='main.Firm'),
        ),
    ]
