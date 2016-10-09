# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from main import constants


def default_data_pop(apps, schema_editor):
    Firm = apps.get_model('main', 'Firm')
    AccountType = apps.get_model('main', 'AccountType')
    ClientAccount = apps.get_model('client', 'ClientAccount')
    db_alias = schema_editor.connection.alias

    # Create all the AccountType Entries in the DB.
    for key, val in constants.ACCOUNT_TYPES:
        AccountType.objects.using(db_alias).create(id=key)

    # Initially Assign the AccountTypes provided by a firm to the ones currently in use, plus personal account
    # as this is the simplest, default case.
    for f in Firm.objects.using(db_alias).all():
        atids = list(ClientAccount.objects.using(db_alias).filter(primary_owner__advisor__firm=f).values_list('account_type',
                                                                                                              flat=True))
        atids.append(constants.ACCOUNT_TYPE_PERSONAL)
        ats = list(AccountType.objects.using(db_alias).filter(id__in=atids))
        f.account_types.add(*ats)


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0060_auto_20160921_0422'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.IntegerField(primary_key=True, choices=[(0, 'Personal Account'), (1, 'Joint Account'), (2, 'Trust Account'), (3, 'Self Managed Superannuation Fund'), (4, 'Corporate Account'), (5, '401K Account'), (6, 'Roth 401K Account'), (7, 'Individual Retirement Account (IRA)'), (8, 'Roth IRA')], serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='firm',
            name='account_types',
            field=models.ManyToManyField(help_text='The set of supported account types offered to clients of this firm.', to='main.AccountType'),
        ),
        migrations.RunPython(default_data_pop),
    ]
