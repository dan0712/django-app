# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('portfolios', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='portfolio_set',
            field=models.ForeignKey(to='portfolios.PortfolioSet'),
        ),
        migrations.AddField(
            model_name='goal',
            name='account',
            field=models.ForeignKey(related_name='goals', to='main.ClientAccount'),
        ),
        migrations.AddField(
            model_name='firmdata',
            name='firm',
            field=models.OneToOneField(to='main.Firm', related_name='firm_details'),
        ),
        migrations.AddField(
            model_name='financialprofile',
            name='client',
            field=models.OneToOneField(to='main.Client', related_name='financial_profile'),
        ),
        migrations.AddField(
            model_name='financialplanexternalaccount',
            name='client',
            field=models.ForeignKey(related_name='financial_plan_external_accounts', to='main.Client'),
        ),
        migrations.AddField(
            model_name='financialplanaccount',
            name='account',
            field=models.ForeignKey(to='main.Goal'),
        ),
        migrations.AddField(
            model_name='financialplanaccount',
            name='client',
            field=models.ForeignKey(related_name='financial_plan_accounts', to='main.Client'),
        ),
        migrations.AddField(
            model_name='financialplan',
            name='client',
            field=models.OneToOneField(to='main.Client', related_name='financial_plan'),
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='inviter_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='account_group',
            field=models.ForeignKey(to='main.AccountGroup', null=True, related_name='accounts'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='primary_owner',
            field=models.ForeignKey(related_name='accounts', to='main.Client'),
        ),
        migrations.AddField(
            model_name='client',
            name='advisor',
            field=models.ForeignKey(related_name='clients', to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='client',
            name='secondary_advisors',
            field=models.ManyToManyField(related_name='secondary_clients', to='main.Advisor', editable=False),
        ),
        migrations.AddField(
            model_name='client',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='automaticwithdrawal',
            name='account',
            field=models.OneToOneField(to='main.Goal', related_name='auto_withdrawal'),
        ),
        migrations.AddField(
            model_name='automaticdeposit',
            name='account',
            field=models.OneToOneField(to='main.Goal', related_name='auto_deposit'),
        ),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='firm',
            field=models.ForeignKey(related_name='authorised_representatives', to='main.Firm'),
        ),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='authorised_representative'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='firm',
            field=models.ForeignKey(related_name='advisors', to='main.Firm'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='advisor'),
        ),
        migrations.AddField(
            model_name='accountgroup',
            name='advisor',
            field=models.ForeignKey(related_name='primary_account_groups', to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='accountgroup',
            name='secondary_advisors',
            field=models.ManyToManyField(related_name='secondary_account_groups', to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', to='auth.Group', blank=True, related_name='user_set', related_query_name='user'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(help_text='Specific permissions for this user.', verbose_name='user permissions', to='auth.Permission', blank=True, related_name='user_set', related_query_name='user'),
        ),
    ]
