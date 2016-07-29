# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0003_auto_20160730_0231'),
        ('main', '0041_user_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounttyperiskprofilegroup',
            name='risk_profile_group',
        ),
        migrations.RemoveField(
            model_name='client',
            name='advisor',
        ),
        migrations.RemoveField(
            model_name='client',
            name='residential_address',
        ),
        migrations.RemoveField(
            model_name='client',
            name='secondary_advisors',
        ),
        migrations.RemoveField(
            model_name='client',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='clientaccount',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='account_group',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='asset_fee_plan',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='default_portfolio_set',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='primary_owner',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='risk_profile_group',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='risk_profile_responses',
        ),
        migrations.RemoveField(
            model_name='clientaccount',
            name='signatories',
        ),
        migrations.AlterUniqueTogether(
            name='riskprofileanswer',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='riskprofileanswer',
            name='question',
        ),
        migrations.AlterUniqueTogether(
            name='riskprofilequestion',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='riskprofilequestion',
            name='group',
        ),
        migrations.AlterField(
            model_name='externalasset',
            name='owner',
            field=models.ForeignKey(related_name='external_assets', to='client.Client'),
        ),
        migrations.AlterField(
            model_name='goal',
            name='account',
            field=models.ForeignKey(related_name='all_goals', to='client.ClientAccount'),
        ),
        migrations.AlterField(
            model_name='marketorderrequest',
            name='account',
            field=models.ForeignKey(related_name='market_orders', to='client.ClientAccount', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='client',
            field=models.ForeignKey(to='client.Client'),
        ),
        migrations.AlterField(
            model_name='retirementplan',
            name='smsf_account',
            field=models.OneToOneField(related_name='retirement_plan', to='client.ClientAccount', help_text='The associated SMSF account.', null=True),
        ),
        migrations.DeleteModel(
            name='AccountTypeRiskProfileGroup',
        ),
        migrations.DeleteModel(
            name='Client',
        ),
        migrations.DeleteModel(
            name='ClientAccount',
        ),
        migrations.DeleteModel(
            name='RiskProfileAnswer',
        ),
        migrations.DeleteModel(
            name='RiskProfileGroup',
        ),
        migrations.DeleteModel(
            name='RiskProfileQuestion',
        ),
    ]
