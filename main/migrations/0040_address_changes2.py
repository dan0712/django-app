# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_address_changes'),
    ]

    operations = [
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
