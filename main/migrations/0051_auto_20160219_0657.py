# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_auto_20160214_0126'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('target', models.FloatField(default=0)),
                ('completion', models.DateField(help_text='The scheduled completion date for the goal.')),
                ('hedge_fx', models.BooleanField(help_text='Do we want to hedge foreign exposure?')),
            ],
        ),
        migrations.CreateModel(
            name='MarketCap',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('value', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('variance', models.FloatField()),
                ('er', models.FloatField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('weight', models.FloatField()),
                ('volatility', models.FloatField(help_text='variance of this asset a the time of setting this portfolio.')),
            ],
        ),
        migrations.CreateModel(
            name='PortfolioSet',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('risk_free_rate', models.FloatField()),
                ('tau', models.FloatField()),
                ('default_region_sizes', models.TextField(default='{}')),
                ('portfolios', models.TextField(null=True, editable=False, blank=True)),
                ('default_picked_regions', models.TextField(null=True)),
                ('optimization_mode', models.IntegerField(default=2, choices=[(1, 'auto mode'), (2, 'weight mode')])),
            ],
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('q', models.FloatField()),
                ('assets', models.TextField()),
                ('portfolio_set', models.ForeignKey(to='main.PortfolioSet', related_name='views')),
            ],
        ),
        migrations.CreateModel(
            name='ProxyAssetClass',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Asset class',
                'verbose_name_plural': 'Asset classes',
            },
            bases=('main.assetclass',),
        ),
        migrations.CreateModel(
            name='ProxyTicker',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Ticker',
                'verbose_name_plural': 'Tickers',
            },
            bases=('main.ticker',),
        ),
        migrations.RenameField(
            model_name='goal',
            old_name='created_date',
            new_name='created',
        ),
        migrations.RemoveField(
            model_name='automaticdeposit',
            name='account',
        ),
        migrations.RemoveField(
            model_name='automaticwithdrawal',
            name='account',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='account_type',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='allocation',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='completion_date',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='custom_hedges',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='custom_optimization_mode',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='custom_picked_regions',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='custom_portfolio_set',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='custom_regions',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='drift',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='ethical_investments',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='income',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='initialDeposit',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='portfolios',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='satellite_pct',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='target',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='total_balance_db',
        ),
        migrations.RemoveField(
            model_name='goal',
            name='type',
        ),
        migrations.RemoveField(
            model_name='goaltypes',
            name='code',
        ),
        migrations.AddField(
            model_name='client',
            name='employment_status_int',
            field=models.IntegerField(null=True, choices=[(0, 'Employed (full-time)'), (1, 'Employed (part-time)'), (1, 'Self-employed'), (2, 'Student'), (3, 'Retired'), (4, 'Homemaker'), (5, 'Not employed')]),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='account_type',
            field=models.IntegerField(null=True, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account')]),
        ),
        migrations.AddField(
            model_name='goal',
            name='type_t',
            field=models.ForeignKey(null=True, to='main.GoalTypes'),
        ),
        migrations.AddField(
            model_name='goaltypes',
            name='risk_sensitivity',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)], default=10, help_text='Default risk sensitivity for this goal type. 0 = not sensitive, 10 = Very sensitive (No risk tolerated)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='type_int',
            field=models.IntegerField(null=True, choices=[(0, 'ALLOCATION'), (1, 'DEPOSIT'), (2, 'WITHDRAWAL'), (3, 'REBALANCE'), (4, 'MARKET_CHANGE'), (5, 'FEE')]),
        ),
        migrations.AlterField(
            model_name='emailinvitation',
            name='invitation_type',
            field=models.PositiveIntegerField(default=3, choices=[(0, 'Advisor'), (1, 'Authorised representative'), (2, 'Supervisor'), (3, 'Client')]),
        ),
        migrations.AlterField(
            model_name='goal',
            name='archived',
            field=models.BooleanField(default=False, help_text='An archived goal is "deleted"'),
        ),
        migrations.AlterField(
            model_name='performer',
            name='portfolio_set',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='platform',
            name='portfolio_set',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(max_length=255, choices=[('ALLOCATION', 'ALLOCATION'), ('DEPOSIT', 'DEPOSIT'), ('WITHDRAWAL', 'WITHDRAWAL'), ('REBALANCE', 'REBALANCE'), ('MARKET_CHANGE', 'MARKET_CHANGE'), ('FEE', 'FEE')]),
        ),
        migrations.AddField(
            model_name='portfolioset',
            name='asset_classes',
            field=models.ManyToManyField(to='main.AssetClass', related_name='portfolio_sets'),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='asset',
            field=models.ForeignKey(to='main.Ticker'),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='portfolio',
            field=models.ForeignKey(to='main.Portfolio', related_name='items'),
        ),
        migrations.AddField(
            model_name='marketcap',
            name='ticker',
            field=models.OneToOneField(to='main.Ticker', related_name='market_cap'),
        ),
        migrations.AddField(
            model_name='goalsetting',
            name='auto_deposit',
            field=models.OneToOneField(null=True, to='main.AutomaticDeposit'),
        ),
        migrations.AddField(
            model_name='goalsetting',
            name='portfolio',
            field=models.OneToOneField(to='main.Portfolio', related_name='goal_setting'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='default_portfolio_set',
            field=models.ForeignKey(null=True, to='main.PortfolioSet'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='default_portfolio_set',
            field=models.ForeignKey(null=True, to='main.PortfolioSet'),
        ),
        migrations.AddField(
            model_name='firm',
            name='default_portfolio_set',
            field=models.ForeignKey(null=True, to='main.PortfolioSet'),
        ),
        migrations.AddField(
            model_name='goal',
            name='active_settings',
            field=models.OneToOneField(null=True, help_text='The settings were last used to do a rebalance. These settings are responsible for our current market positions.', to='main.GoalSetting', related_name='goal_active'),
        ),
        migrations.AddField(
            model_name='goal',
            name='approved_settings',
            field=models.OneToOneField(null=True, help_text='The settings that both the client and advisor have confirmed and will become active the next time the goal is rebalanced.', to='main.GoalSetting', related_name='goal_approved'),
        ),
        migrations.AddField(
            model_name='goal',
            name='portfolio_set',
            field=models.ForeignKey(null=True, help_text='The set of assets that may be used to create a portfolio for this goal.', to='main.PortfolioSet'),
        ),
        migrations.AddField(
            model_name='goal',
            name='selected_settings',
            field=models.OneToOneField(null=True, help_text='The settings that the client has confirmed, but are not yet approved by the advisor.', to='main.GoalSetting', related_name='goal_selected'),
        ),
    ]
