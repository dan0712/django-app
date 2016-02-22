# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160220_2215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringtransaction',
            name='last_plan_change',
        ),
        migrations.AlterField(
            model_name='goal',
            name='active_settings',
            field=models.OneToOneField(related_name='goal_active', help_text='The settings were last used to do a rebalance. These settings are responsible for our current market positions.', null=True, to='main.GoalSetting', blank=True),
        ),
        migrations.AlterField(
            model_name='goal',
            name='approved_settings',
            field=models.OneToOneField(related_name='goal_approved', help_text='The settings that both the client and advisor have confirmed and will become active the next time the goal is rebalanced.', null=True, to='main.GoalSetting', blank=True),
        ),
        migrations.AlterField(
            model_name='goal',
            name='selected_settings',
            field=models.OneToOneField(related_name='goal_selected', help_text='The settings that the client has confirmed, but are not yet approved by the advisor.', null=True, to='main.GoalSetting', blank=True),
        ),
        migrations.AlterField(
            model_name='portfolioitem',
            name='volatility',
            field=models.FloatField(help_text='variance of this asset at the time of creating this portfolio.'),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='recurrence',
            field=models.TextField(),
        ),
    ]
