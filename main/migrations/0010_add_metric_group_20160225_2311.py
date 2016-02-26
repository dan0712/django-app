# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def check_db(apps, schema_editor):
    GoalMetric = apps.get_model("main", "GoalMetric")
    Portfolio = apps.get_model("main", "Portfolio")
    PortfolioItem = apps.get_model("main", "PortfolioItem")
    db_alias = schema_editor.connection.alias

    invalid_metrics = list(GoalMetric.objects.using(db_alias).filter(setting=None).values_list('id', flat=True))
    if len(invalid_metrics) > 0:
        raise Exception('GoalMetric ids: {} are orphaned (they have no settings object, so cannot be used. Please delete them.'.format(invalid_metrics))

    invalid_portfolios = list(Portfolio.objects.using(db_alias).filter(goal_setting=None).values_list('id', flat=True))
    if len(invalid_portfolios) > 0:
        ipis = list(PortfolioItem.objects.using(db_alias).filter(portfolio__in=invalid_portfolios).values_list('id', flat=True))
        raise Exception('Portfolio ids: {} are orphaned (they have no settings object, so cannot be used.'
                        'Their portfolioitem ids: {} are also orphaned. Please delete them both.'.format(invalid_portfolios, ipis))


def set_group(apps, schema_editor):
    GoalSetting = apps.get_model("main", "GoalSetting")
    GoalMetricGroup = apps.get_model("main", "GoalMetricGroup")
    db_alias = schema_editor.connection.alias
    for setting in GoalSetting.objects.using(db_alias).all():
        metric_group = GoalMetricGroup.objects.using(db_alias).create()
        for metric in setting.metrics.using(db_alias).all():
            metric.group = metric_group
            metric.setting = None
            metric.save()
        setting.metric_group = metric_group
        setting.save()


def set_portfolio(apps, schema_editor):
    GoalSetting = apps.get_model("main", "GoalSetting")
    db_alias = schema_editor.connection.alias
    for setting in GoalSetting.objects.using(db_alias).all():
        setting.portfolio.setting = setting
        setting.portfolio.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20160224_1934'),
    ]

    operations = [
        migrations.RunPython(check_db),
        migrations.AlterField(
            model_name='goal',
            name='active_settings',
            field=models.OneToOneField(help_text='The settings were last used to do a rebalance.These settings are responsible for our current market positions.', to='main.GoalSetting', null=True, related_name='goal_active', blank=True),
        ),
        migrations.AlterField(
            model_name='goalsetting',
            name='portfolio',
            field=models.ForeignKey(to='main.Portfolio', related_name='settings'),
        ),
        migrations.CreateModel(
            name='GoalMetricGroup',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type', models.IntegerField(default=0, choices=[(0, 'Custom'), (1, 'Preset')])),
                ('name', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='goalmetric',
            name='group',
            field=models.ForeignKey(null=True, to='main.GoalMetricGroup', related_name='metrics'),
        ),
        migrations.AddField(
            model_name='goalsetting',
            name='metric_group',
            field=models.ForeignKey(null=True, to='main.GoalMetricGroup', related_name='settings'),
        ),
        migrations.RunPython(set_group),
        migrations.AlterField(
            model_name='goalmetric',
            name='group',
            field=models.ForeignKey(to='main.GoalMetricGroup', related_name='metrics'),
        ),
        migrations.AlterField(
            model_name='goalsetting',
            name='metric_group',
            field=models.ForeignKey(to='main.GoalMetricGroup', related_name='settings'),
        ),
        migrations.RemoveField(
            model_name='goalmetric',
            name='setting',
        ),
        migrations.AddField(
            model_name='portfolio',
            name='setting',
            field=models.OneToOneField(null=True, related_name='nportfolio', to='main.GoalSetting'),
        ),
        migrations.RunPython(set_portfolio),
        migrations.RemoveField(
            model_name='goalsetting',
            name='portfolio',
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='setting',
            field=models.OneToOneField(to='main.GoalSetting', related_name='portfolio'),
        ),
    ]
