# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from main.models import PortfolioSet

default_portfolio_set = PortfolioSet.objects.get(name='Default')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_auto_20160219_0921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='employment_status',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='account_class',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='type',
        ),
        migrations.AlterField(
            model_name='firm',
            name='default_portfolio_set',
            field=models.ForeignKey(to='main.PortfolioSet',  default=default_portfolio_set.id),
        ),
        migrations.AlterField(
            model_name='goal',
            name='type',
            field=models.ForeignKey(to='main.GoalTypes'),
        ),
    ]
