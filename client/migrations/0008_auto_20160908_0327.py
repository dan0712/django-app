# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def def_rpg(apps, schema_editor):
    from main import constants
    Client = apps.get_model("client", "Client")
    RiskProfileGroup = apps.get_model("client", "RiskProfileGroup")
    db_alias = schema_editor.connection.alias

    # First create the default risk profile groups for natural and corporate entities.
    def_nat = RiskProfileGroup.objects.create(name='default_natural',
                                              description='The default risk profile questions for clients')

    for client in Client.objects.using(db_alias).all():
        personal_accounts = client.primary_accounts.filter(account_type=constants.ACCOUNT_TYPE_PERSONAL)
        if personal_accounts.count():
            account = personal_accounts.all()[0]
            client.risk_profile_group = account.risk_profile_group
            for response in account.risk_profile_responses.all():
                client.risk_profile_responses.add(response)
        else:
            client.risk_profile_group = def_nat
        client.save()

class Migration(migrations.Migration):

    dependencies = [
        ('client', '0007_auto_20160908_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='risk_profile_group',
            field=models.ForeignKey(null=True, to='client.RiskProfileGroup',
                                    related_name='clients'),
        ),
        migrations.AddField(
            model_name='client',
            name='risk_profile_responses',
            field=models.ManyToManyField(to='client.RiskProfileAnswer'),
        ),
        migrations.RunPython(def_rpg),
        migrations.AlterField(
            model_name='clientaccount',
            name='risk_profile_group',
            field=models.ForeignKey(related_name='accounts', to='client.RiskProfileGroup'),
        ),
    ]
