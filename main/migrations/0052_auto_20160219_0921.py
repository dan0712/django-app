# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from main.models import Transaction, ACCOUNT_TYPE_PERSONAL, \
    ACCOUNT_TYPE_TRUST, ClientAccount, Client, EMPLOYMENT_STATUS_UNEMPLOYED, GoalTypes

JOINT_ACCOUNT = "joint_account"
TRUST_ACCOUNT = "trust_account"

ALLOCATION = "ALLOCATION"
DEPOSIT = "DEPOSIT"
WITHDRAWAL = "WITHDRAWAL"
FEE = "FEE"
REBALANCE = "REBALANCE"
MARKET_CHANGE = "MARKET_CHANGE"
TRANSACTION_TYPES = (
    (REBALANCE, 'REBALANCE'),
    (ALLOCATION, "ALLOCATION"),
    (DEPOSIT, "DEPOSIT"),
    (WITHDRAWAL, 'WITHDRAWAL'),
    (MARKET_CHANGE, "MARKET_CHANGE"),
    (FEE, "FEE")
)

FULL_TIME = "FULL_TIME"
PART_TIME = 'PART_TIME'
SELF_EMPLOYED = 'SELF_EMPLOYED'
STUDENT = "STUDENT"
RETIRED = "RETIRED"
HOMEMAKER = "HOMEMAKER"
UNEMPLOYED = "UNEMPLOYED"

EMPLOYMENT_STATUS_CHOICES = (
    (FULL_TIME, 'Employed (full-time)'),
    (PART_TIME, 'Employed (part-time)'),
    (SELF_EMPLOYED, 'Self-employed'),
    (STUDENT, 'Student'),
    (RETIRED, 'Retired'),
    (HOMEMAKER, 'Homemaker'),
    (UNEMPLOYED, "Not employed")
)
tts_to_tti = {v[0]: i for i, v in enumerate(TRANSACTION_TYPES)}
ats_to_ati = {
    # Yes, this is strange, but that's the way it was...
    JOINT_ACCOUNT: ACCOUNT_TYPE_PERSONAL,
    TRUST_ACCOUNT: ACCOUNT_TYPE_TRUST
}
esc_to_es = {v[0]: i for i, v in enumerate(EMPLOYMENT_STATUS_CHOICES)}
esc_to_es[''] = EMPLOYMENT_STATUS_UNEMPLOYED

other_goal_type, created = GoalTypes.objects.get_or_create(name='other',
                                                           defaults={'default_term': 10,
                                                                     'group':  'Other',
                                                                     'risk_sensitivity': 5})


def copy_fields(apps, schema_editor):
    for tx in Transaction.objects.all():
        tx.type_int = tts_to_tti[tx.type]
        tx.save()
    for ca in ClientAccount.objects.all():
        ca.account_type = ats_to_ati[ca.account_class]
        ca.save()
    for cl in Client.objects.all():
        cl.employment_status_int = esc_to_es[cl.employment_status]
        cl.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20160219_0657'),
    ]

    operations = [
        migrations.RunPython(copy_fields),
        migrations.RenameField(
            model_name='goal',
            old_name='type_t',
            new_name='type',
        ),
        migrations.AlterField(
            model_name='goal',
            name='type',
            field=models.ForeignKey(to='main.GoalTypes', default=other_goal_type.id),
        ),
        migrations.AlterField(
            model_name='goal',
            name='portfolio_set',
            field=models.ForeignKey(help_text='The set of assets that may be used to create a portfolio for this goal.',
                                    to='main.PortfolioSet'),
        ),
        migrations.AlterField(
            model_name='platform',
            name='portfolio_set',
            field=models.ForeignKey(to='main.PortfolioSet'),
        ),
    ]
