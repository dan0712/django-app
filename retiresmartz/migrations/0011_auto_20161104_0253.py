# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0066_auto_20161104_0253'),
        ('retiresmartz', '0010_auto_20161102_0044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='retirementplan',
            name='portfolio',
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='goal_setting',
            field=models.OneToOneField(to='main.GoalSetting', null=True, related_name='retirement_plan', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
