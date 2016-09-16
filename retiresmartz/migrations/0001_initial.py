# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_auto_20160917_0623'),
        ('client', '0012_auto_20160917_0449'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetirementLifestyle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('cost', models.PositiveIntegerField(help_text="The expected cost in system currency of this lifestyle in today's dollars")),
                ('holidays', models.TextField(help_text='The text for the holidays block')),
                ('eating_out', models.TextField(help_text='The text for the eating out block')),
                ('health', models.TextField(help_text='The text for the health block')),
                ('interests', models.TextField(help_text='The text for the interests block')),
                ('leisure', models.TextField(help_text='The text for the leisure block')),
                ('default_volunteer_days', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], help_text='The default number of volunteer work days selected for this lifestyle', default=0)),
                ('default_paid_days', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], help_text='The default number of paid work days selected for this lifestyle', default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RetirementPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('lifestyle', models.PositiveIntegerField(help_text='The desired retirement lifestyle', choices=[(1, 'Doing OK'), (2, 'Comfortable'), (3, 'Doing Well'), (4, 'Luxury')], default=1)),
                ('desired_income', models.PositiveIntegerField(help_text='The desired annual household pre-tax retirement income in system currency', default=60000)),
                ('current_income', models.PositiveIntegerField(help_text='The current annual household pre-tax income at the start of your plan', default=0)),
                ('volunteer_days', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], help_text='The number of volunteer work days selected', default=0)),
                ('paid_days', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(7)], help_text='The number of paid work days selected', default=0)),
                ('same_home', models.BooleanField(help_text='Will you be retiring in the same home?', default=True)),
                ('retirement_postal_code', models.CharField(validators=[django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(10)], help_text='What postal code will you retire in?', null=True, blank=True, max_length=10)),
                ('reverse_mortgage', models.NullBooleanField(help_text='Would you consider a reverse mortgage? (optional)')),
                ('retirement_home_style', models.PositiveIntegerField(help_text='The style of your retirement home', choices=[(1, 'Single, Detached'), (2, 'Single, Attached'), (3, 'Multi-Unit, 9 or less'), (4, 'Multi-Unit, 10 - 20'), (5, 'Multi-Unit, 20+'), (6, 'Mobile Home'), (7, 'RV, Van, Boat, etc')], default=1)),
                ('retirement_home_price', models.PositiveIntegerField(help_text="The price of your future retirement home (in today's dollars)", default=0)),
                ('beta_spouse', models.BooleanField(help_text="Will BetaSmartz manage your spouse's retirement assets as well?", default=False)),
                ('expenses', jsonfield.fields.JSONField(help_text='List of expenses [{id, desc, cat, who, amt},...]', null=True, blank=True)),
                ('savings', jsonfield.fields.JSONField(help_text='List of savings [{id, desc, cat, who, amt},...]', null=True, blank=True)),
                ('initial_deposits', jsonfield.fields.JSONField(help_text='List of deposits [{id, desc, cat, who, amt},...]', null=True, blank=True)),
                ('income_growth', models.FloatField(help_text='Above CPI', default=0)),
                ('expected_return_confidence', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], default=0.5)),
                ('retirement_age', models.PositiveIntegerField(default=65)),
                ('max_match', models.FloatField(help_text='The percent the employer matches of before-tax contributions', null=True, blank=True)),
                ('desired_risk', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], help_text='The selected risk appetite for this retirement plan', default=0)),
                ('recommended_risk', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], help_text='The calculated recommended risk for this retirement plan', default=0)),
                ('max_risk', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], help_text='The maximum allowable risk appetite for this retirement plan, based on our risk model', default=0)),
                ('calculated_life_expectancy', models.PositiveIntegerField(default=65)),
                ('selected_life_expectancy', models.PositiveIntegerField(default=65)),
                ('agreed_on', models.DateTimeField(null=True, blank=True)),
                ('portfolio', jsonfield.fields.JSONField(null=True, blank=True)),
                ('partner_data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('client', models.ForeignKey(to='client.Client')),
                ('partner_plan', models.OneToOneField(on_delete=django.db.models.deletion.SET_NULL, null=True, to='retiresmartz.RetirementPlan', related_name='partner_plan_reverse')),
                ('smsf_account', models.OneToOneField(null=True, help_text='The associated SMSF account.', to='client.ClientAccount', related_name='retirement_plan')),
            ],
        ),
        migrations.CreateModel(
            name='RetirementPlanATC',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField(help_text='RRULE to specify when the transfer happens')),
                ('plan', models.OneToOneField(to='retiresmartz.RetirementPlan', related_name='atc')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RetirementPlanBTC',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(help_text='Daily rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField(help_text='RRULE to specify when the transfer happens')),
                ('plan', models.OneToOneField(to='retiresmartz.RetirementPlan', related_name='btc')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RetirementSpendingGoal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('goal', models.OneToOneField(to='main.Goal', related_name='retirement_plan')),
                ('plan', models.ForeignKey(to='retiresmartz.RetirementPlan', related_name='retirement_goals')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='retirementplan',
            unique_together=set([('name', 'client')]),
        ),
    ]
