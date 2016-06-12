# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20160602_1945'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetirementPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('begin_date', models.DateField(help_text='Date the retirement plan is supposed to begin.', auto_now_add=True)),
                ('retirement_date', models.DateField()),
                ('life_expectancy', models.IntegerField(help_text='Until what age do we want to plan retirement spending?')),
                ('spendable_income', models.IntegerField(help_text='The current annual spendable income. This must be identical across partner plans as they have a common spendable income.', default=0)),
                ('desired_income', models.IntegerField(help_text='The desired annual spendable income in retirement', default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RetirementPlanExternalIncome',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TransferPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(help_text='Annualized rate to increase or decrease the amount by as of the begin_date')),
                ('schedule', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='financialprofile',
            name='marital_status',
        ),
        migrations.AddField(
            model_name='advisor',
            name='civil_status',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='civil_status',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='civil_status',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='retirementplanexternalincome',
            name='income',
            field=models.OneToOneField(related_name='retirement_plan_einc', to='main.TransferPlan'),
        ),
        migrations.AddField(
            model_name='retirementplanexternalincome',
            name='plan',
            field=models.ForeignKey(to='main.RetirementPlan', related_name='external_income'),
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='atc',
            field=models.OneToOneField(related_name='retirement_plan_atc', to='main.TransferPlan', help_text='The after tax contributions into the retirement account until retirement date'),
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='btc',
            field=models.OneToOneField(related_name='retirement_plan_btc', to='main.TransferPlan', help_text='The before tax contributions into the retirement account until retirement date'),
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='client',
            field=models.ForeignKey(to='main.Client'),
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='partner_plan',
            field=models.OneToOneField(null=True, related_name='partner_plan_reverse', to='main.RetirementPlan', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AddField(
            model_name='retirementplan',
            name='smsf_account',
            field=models.OneToOneField(null=True, related_name='retirement_plan', to='main.ClientAccount', help_text='The associated SMSF account.'),
        ),
        migrations.AlterUniqueTogether(
            name='retirementplan',
            unique_together=set([('name', 'client')]),
        ),
    ]
