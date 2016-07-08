# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import phonenumber_field.modelfields


def migrate_data(apps, schema_editor):
    RetirementPlan = apps.get_model("main", "RetirementPlan")
    Client = apps.get_model("main", "Client")
    FirmData = apps.get_model("main", "FirmData")
    Advisor = apps.get_model("main", "Advisor")
    Address = apps.get_model("address", "Address")
    Region = apps.get_model("address", "Region")
    AuthorisedRepresentative = apps.get_model("main", "AuthorisedRepresentative")
    SecurityAnswer = apps.get_model("user", "SecurityAnswer")

    db_alias = schema_editor.connection.alias

    def _get_address(add_1, add_2, city, state, zip):
        raw = "{}\n{}\n{}".format(add_1, add_2, city)

        region = Region.objects.using(db_alias).get_or_create(code=state, country='AU', defaults={'name': state})[0]

        return Address.objects.using(db_alias).create(address=raw, region=region, post_code=zip)

    def _do_personal_data(pd):
        pd.residential_address = _get_address(pd.address_line_1,
                                              pd.address_line_2,
                                              pd.city,
                                              pd.state,
                                              pd.post_code)
        if pd.phone_number is not None:
            pd.phone_num = '+61{}'.format(int(pd.phone_number))

        # Convert the security questions to their own model.
        if len(pd.security_answer_1) > 0:
            SecurityAnswer.objects.using(db_alias).create(user=pd.user,
                                                          question=pd.security_question_1,
                                                          answer=pd.security_answer_1)
        if len(pd.security_answer_2) > 0:
            SecurityAnswer.objects.using(db_alias).create(user=pd.user,
                                                          question=pd.security_question_2,
                                                          answer=pd.security_answer_2)

    for client in Client.objects.using(db_alias).all():
        _do_personal_data(client)
        client.save()

    for advisor in Advisor.objects.using(db_alias).all():
        _do_personal_data(advisor)
        if advisor.work_phone is not None:
            advisor.work_phone_num = '+61{}'.format(int(advisor.work_phone))
        advisor.save()

    for rep in AuthorisedRepresentative.objects.using(db_alias).all():
        _do_personal_data(rep)
        rep.save()

    for fd in FirmData.objects.using(db_alias).all():
        fd.office_address = _get_address(fd.office_address_line_1,
                                         fd.office_address_line_2,
                                         fd.office_city,
                                         fd.office_state,
                                         fd.office_post_code)
        fd.postal_address = _get_address(fd.postal_address_line_1,
                                         fd.postal_address_line_2,
                                         fd.postal_city,
                                         fd.postal_state,
                                         fd.postal_post_code)
        fd.daytime_phone_num = '+61{}'.format(int(fd.daytime_phone_number))
        fd.mobile_phone_num = '+61{}'.format(int(fd.mobile_phone_number))
        fd.fax_num = '+61{}'.format(int(fd.fax_number))
        fd.save()

    for plan in RetirementPlan.objects.using(db_alias).all().select_related('btc', 'atc').prefetch_related('external_income'):
        plan.btc.owner = plan
        plan.btc.label = 'btcs'
        plan.btc.save()
        plan.atc.owner = plan
        plan.atc.label = 'atcs'
        plan.atc.save()
        for inc in plan.external_income:
            inc.income.owner = plan
            inc.income.label = 'external_incomes'
            inc.income.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('address', '0001_initial'),
        ('main', '0038_accounttyperiskprofilegroup'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('type', models.IntegerField(choices=[(0, 'Family Home'), (1, 'Investment Property'), (2, 'Investment Portfolio'), (3, 'Savings Account'), (4, 'Property Loan'), (5, 'Transaction Account'), (6, 'Retirement Account'), (7, 'Other')])),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('valuation', models.DecimalField(help_text='In the system currency. Could be negative if a debt', max_digits=15, decimal_places=2)),
                ('valuation_date', models.DateField(help_text='Date when the asset was valued')),
                ('growth', models.DecimalField(help_text='Modeled annualized growth of the asset - pos or neg. 0.0 is no growth', max_digits=5, decimal_places=4)),
                ('acquisition_date', models.DateField(help_text="Could be in the future if it's a future acquisition")),
            ],
        ),
        migrations.DeleteModel(
            name='CostOfLivingIndex',
        ),
        migrations.RemoveField(
            model_name='financialplan',
            name='client',
        ),
        migrations.RemoveField(
            model_name='financialplanaccount',
            name='account',
        ),
        migrations.RemoveField(
            model_name='financialplanaccount',
            name='client',
        ),
        migrations.RemoveField(
            model_name='financialplanexternalaccount',
            name='client',
        ),
        migrations.RemoveField(
            model_name='financialprofile',
            name='client',
        ),
        migrations.AddField(
            model_name='advisor',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='advisor',
            name='residential_address',
            field=models.ForeignKey(null=True, to='address.Address', related_name='+'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='work_phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='residential_address',
            field=models.ForeignKey(null=True, to='address.Address', related_name='+'),
        ),
        migrations.AddField(
            model_name='client',
            name='phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='residential_address',
            field=models.ForeignKey(null=True, to='address.Address', related_name='+'),
        ),
        migrations.AddField(
            model_name='firmdata',
            name='daytime_phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='firmdata',
            name='fax_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='firmdata',
            name='mobile_phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='firmdata',
            name='office_address',
            field=models.ForeignKey(null=True, to='address.Address', related_name='+'),
        ),
        migrations.AddField(
            model_name='firmdata',
            name='postal_address',
            field=models.ForeignKey(null=True, to='address.Address', related_name='+'),
        ),
        migrations.AddField(
            model_name='transferplan',
            name='label',
            field=models.CharField(max_length=32, null=True, help_text='A label to disambiguate the objects when a TransferPlan is used for multiple fields on the same owner_type. Set this to the field name on the owner'),
        ),
        migrations.AddField(
            model_name='transferplan',
            name='owner_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='transferplan',
            name='owner_type',
            field=models.ForeignKey(null=True, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='civil_status',
            field=models.IntegerField(null=True, choices=[(0, 'SINGLE'), (1, 'MARRIED')]),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='civil_status',
            field=models.IntegerField(null=True, choices=[(0, 'SINGLE'), (1, 'MARRIED')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='civil_status',
            field=models.IntegerField(null=True, choices=[(0, 'SINGLE'), (1, 'MARRIED')]),
        ),
        migrations.AlterField(
            model_name='transferplan',
            name='growth',
            field=models.FloatField(help_text='Annualized rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change'),
        ),
        migrations.CreateModel(
            name='ExternalAccount',
            fields=[
                ('externalasset_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, to='main.ExternalAsset', serialize=False)),
                ('institution', models.CharField(max_length=128, help_text='Institute where the account is held.')),
                ('account_id', models.CharField(max_length=64)),
            ],
            bases=('main.externalasset',),
        ),
        migrations.DeleteModel(
            name='FinancialPlan',
        ),
        migrations.DeleteModel(
            name='FinancialPlanAccount',
        ),
        migrations.DeleteModel(
            name='FinancialPlanExternalAccount',
        ),
        migrations.DeleteModel(
            name='FinancialProfile',
        ),
        migrations.AddField(
            model_name='externalasset',
            name='debt',
            field=models.OneToOneField(help_text='Any debt that is directly associated to the asset.', to='main.ExternalAsset', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='for_asset'),
        ),
        migrations.AddField(
            model_name='externalasset',
            name='owner',
            field=models.ForeignKey(to='main.Client', related_name='external_assets'),
        ),
        migrations.AlterUniqueTogether(
            name='externalasset',
            unique_together=set([('name', 'owner')]),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name='retirementplanexternalincome',
            name='income',
        ),
        migrations.RemoveField(
            model_name='retirementplanexternalincome',
            name='plan',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='address_line_1',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='city',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='post_code',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='security_answer_1',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='security_answer_2',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='security_question_1',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='security_question_2',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='state',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='work_phone',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='address_line_1',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='city',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='post_code',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='security_answer_1',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='security_answer_2',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='security_question_1',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='security_question_2',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='state',
        ),
        migrations.RemoveField(
            model_name='client',
            name='address_line_1',
        ),
        migrations.RemoveField(
            model_name='client',
            name='address_line_2',
        ),
        migrations.RemoveField(
            model_name='client',
            name='city',
        ),
        migrations.RemoveField(
            model_name='client',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='post_code',
        ),
        migrations.RemoveField(
            model_name='client',
            name='security_answer_1',
        ),
        migrations.RemoveField(
            model_name='client',
            name='security_answer_2',
        ),
        migrations.RemoveField(
            model_name='client',
            name='security_question_1',
        ),
        migrations.RemoveField(
            model_name='client',
            name='security_question_2',
        ),
        migrations.RemoveField(
            model_name='client',
            name='state',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='daytime_phone_number',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='fax_number',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='mobile_phone_number',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='office_address_line_1',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='office_address_line_2',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='office_city',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='office_post_code',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='office_state',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='postal_address_line_1',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='postal_address_line_2',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='postal_city',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='postal_post_code',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='postal_state',
        ),
        migrations.RemoveField(
            model_name='firmdata',
            name='same_address',
        ),
        migrations.RemoveField(
            model_name='retirementplan',
            name='atc',
        ),
        migrations.RemoveField(
            model_name='retirementplan',
            name='btc',
        ),
        migrations.AlterField(
            model_name='advisor',
            name='residential_address',
            field=models.ForeignKey(to='address.Address', related_name='+'),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='residential_address',
            field=models.ForeignKey(to='address.Address', related_name='+'),
        ),
        migrations.AlterField(
            model_name='client',
            name='residential_address',
            field=models.ForeignKey(to='address.Address', related_name='+'),
        ),
        migrations.AlterField(
            model_name='dailyprice',
            name='instrument_content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='dailyprice',
            name='instrument_object_id',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='daytime_phone_num',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='office_address',
            field=models.ForeignKey(to='address.Address', related_name='+'),
        ),
        migrations.AlterField(
            model_name='firmdata',
            name='postal_address',
            field=models.ForeignKey(to='address.Address', related_name='+'),
        ),
        migrations.AlterField(
            model_name='marketcap',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='marketcap',
            name='instrument_content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='marketcap',
            name='instrument_object_id',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='marketindex',
            name='data_api',
            field=models.CharField(help_text='The module that will be used to get the data for this ticker',
                                   max_length=30, choices=[('portfolios.api.bloomberg', 'Bloomberg')]),
        ),
        migrations.AlterField(
            model_name='marketindex',
            name='data_api_param',
            field=models.CharField(
                help_text='Structured parameter string appropriate for the data api. The first component would probably be id appropriate for the given api',
                max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='recurringtransaction',
            name='setting',
            field=models.ForeignKey(to='main.GoalSetting', related_name='recurring_transactions'),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='benchmark_content_type',
            field=models.ForeignKey(verbose_name='Benchmark Type', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='data_api',
            field=models.CharField(help_text='The module that will be used to get the data for this ticker',
                                   max_length=30, choices=[('portfolios.api.bloomberg', 'Bloomberg')]),
        ),
        migrations.AlterField(
            model_name='ticker',
            name='data_api_param',
            field=models.CharField(
                help_text='Structured parameter string appropriate for the data api. The first component would probably be id appropriate for the given api',
                max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name='transferplan',
            name='label',
            field=models.CharField(
                help_text='A label to disambiguate the objects when a TransferPlan is used for multiple fields on the same owner_type. Set this to the field name on the owner',
                max_length=32),
        ),
        migrations.AlterField(
            model_name='transferplan',
            name='owner_id',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='transferplan',
            name='owner_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.DeleteModel(
            name='RetirementPlanExternalIncome',
        ),
        migrations.CreateModel(
            name='ExternalAssetTransfer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(
                    help_text='Annualized rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField()),
                ('asset', models.OneToOneField(related_name='transfer_plan', to='main.ExternalAsset')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RetirementPlanATC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(
                    help_text='Annualized rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField()),
                ('plan', models.OneToOneField(related_name='atc', to='main.RetirementPlan')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RetirementPlanBTC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(
                    help_text='Annualized rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField()),
                ('plan', models.OneToOneField(related_name='btc', to='main.RetirementPlan')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RetirementPlanEinc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('begin_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('growth', models.FloatField(
                    help_text='Annualized rate to increase or decrease the amount by as of the begin_date. 0.0 for no modelled change')),
                ('schedule', models.TextField()),
                ('plan', models.ForeignKey(to='main.RetirementPlan', related_name='external_income')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='transferplan',
            name='owner_type',
        ),
        migrations.DeleteModel(
            name='TransferPlan',
        ),
    ]
