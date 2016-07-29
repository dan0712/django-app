# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountTypeRiskProfileGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('account_type', models.IntegerField(choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account')], unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('date_of_birth', models.DateField(null=True, verbose_name='Date of birth')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=20)),
                ('phone_num', phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True)),
                ('medicare_number', models.CharField(default='', max_length=50)),
                ('civil_status', models.IntegerField(choices=[(0, 'SINGLE'), (1, 'MARRIED')], null=True)),
                ('is_accepted', models.BooleanField(editable=False, default=False)),
                ('confirmation_key', models.CharField(editable=False, blank=True, max_length=36, null=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('client_agreement', models.FileField(upload_to='')),
                ('tax_file_number', models.CharField(blank=True, max_length=9, null=True)),
                ('provide_tfn', models.IntegerField(choices=[(0, 'Yes'), (1, 'I am a non-resident of Australia'), (2, 'I want to claim an exemption'), (3, 'I do not want to quote a Tax File Number or exemption')], default=0, verbose_name='Provide TFN?')),
                ('associated_to_broker_dealer', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='Are employed by or associated with a broker dealer?')),
                ('ten_percent_insider', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='Are you a 10% shareholder, director, or policy maker of a publicly traded company?')),
                ('public_position_insider', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='Do you or a family member hold a public office position?')),
                ('us_citizen', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='Are you a US citizen/person for the purpose of US Federal Income Tax?')),
                ('employment_status', models.IntegerField(choices=[(0, 'Employed (full-time)'), (1, 'Employed (part-time)'), (2, 'Self-employed'), (3, 'Student'), (4, 'Retired'), (5, 'Homemaker'), (6, 'Not employed')], blank=True, null=True)),
                ('net_worth', models.FloatField(default=0, verbose_name='Net worth ($)')),
                ('income', models.FloatField(default=0, verbose_name='Income ($)')),
                ('occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('employer', models.CharField(blank=True, max_length=255, null=True)),
                ('betasmartz_agreement', models.BooleanField(default=False)),
                ('advisor_agreement', models.BooleanField(default=False)),
                ('last_action', models.DateTimeField(null=True)),
                ('advisor', models.ForeignKey(related_name='all_clients', to='main.Advisor', on_delete=django.db.models.deletion.PROTECT)),
                ('residential_address', models.ForeignKey(related_name='+', to='address.Address')),
                ('secondary_advisors', models.ManyToManyField(editable=False, related_name='secondary_clients', to='main.Advisor')),
                ('user', models.OneToOneField(related_name='client', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('custom_fee', models.PositiveIntegerField(default=0)),
                ('account_type', models.IntegerField(choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account')])),
                ('account_name', models.CharField(default='PERSONAL', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('token', models.CharField(editable=False, max_length=36)),
                ('confirmed', models.BooleanField(default=False)),
                ('tax_loss_harvesting_consent', models.BooleanField(default=False)),
                ('tax_loss_harvesting_status', models.CharField(choices=[('USER_OFF', 'USER_OFF'), ('USER_ON', 'USER_ON')], default='USER_OFF', max_length=255)),
                ('cash_balance', models.FloatField(help_text='The amount of cash in this account available to be used.', default=0)),
                ('supervised', models.BooleanField(help_text='Is this account supervised by an advisor?', default=True)),
                ('account_group', models.ForeignKey(related_name='accounts_all', to='main.AccountGroup', null=True)),
                ('asset_fee_plan', models.ForeignKey(to='main.AssetFeePlan', null=True)),
                ('default_portfolio_set', models.ForeignKey(to='main.PortfolioSet')),
                ('primary_owner', models.ForeignKey(related_name='primary_accounts', to='client.Client')),
            ],
        ),
        migrations.CreateModel(
            name='RiskProfileAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('order', models.IntegerField()),
                ('text', models.TextField()),
                ('score', models.FloatField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='RiskProfileGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RiskProfileQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('order', models.IntegerField()),
                ('text', models.TextField()),
                ('group', models.ForeignKey(related_name='questions', to='client.RiskProfileGroup')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='riskprofileanswer',
            name='question',
            field=models.ForeignKey(related_name='answers', to='client.RiskProfileQuestion'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='risk_profile_group',
            field=models.ForeignKey(related_name='accounts', to='client.RiskProfileGroup'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='risk_profile_responses',
            field=models.ManyToManyField(to='client.RiskProfileAnswer'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='signatories',
            field=models.ManyToManyField(help_text='Other clients authorised to operate the account.', related_name='signatory_accounts', to='client.Client'),
        ),
        migrations.AddField(
            model_name='accounttyperiskprofilegroup',
            name='risk_profile_group',
            field=models.ForeignKey(related_name='account_types', to='client.RiskProfileGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='riskprofilequestion',
            unique_together=set([('group', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='riskprofileanswer',
            unique_together=set([('question', 'order')]),
        ),
        migrations.AlterUniqueTogether(
            name='clientaccount',
            unique_together=set([('primary_owner', 'account_name')]),
        ),
    ]
