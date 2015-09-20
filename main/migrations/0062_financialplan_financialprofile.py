# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0061_costoflivingindex'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinancialPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('other_retirement_income_cents', models.FloatField(default=0)),
                ('complete', models.BooleanField(default=False)),
                ('retirement_zip', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('income_replacement_ratio', models.FloatField(default=0)),
                ('client', models.ForeignKey(related_name='financial_plans', to='main.ClientAccount')),
            ],
        ),
        migrations.CreateModel(
            name='FinancialProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('complete', models.BooleanField(default=False)),
                ('marital_status', models.CharField(max_length=100, default='single')),
                ('retired', models.BooleanField(default=False)),
                ('life_expectancy', models.FloatField(null=True, default=70)),
                ('pretax_income_cents', models.FloatField(null=True, default=0)),
                ('social_security_monthly_amount_cents', models.FloatField(null=True, default=0)),
                ('expected_inflation', models.FloatField(default=2.5)),
                ('social_security_percent_expected', models.FloatField(null=True, default=0)),
                ('annual_salary_percent_growth', models.FloatField(null=True, default=0)),
                ('average_tax_percent', models.FloatField(null=True, default=0)),
                ('spouse_name', models.CharField(max_length=100)),
                ('spouse_estimated_birthdate', models.DateTimeField()),
                ('spouse_retired', models.BooleanField(default=False)),
                ('spouse_life_expectancy', models.FloatField(null=True, default=80)),
                ('spouse_pretax_income_cents', models.FloatField(null=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.OneToOneField(to='main.ClientAccount', related_name='financial_profile')),
            ],
        ),
    ]
