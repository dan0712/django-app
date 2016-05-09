# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from django.db import models, migrations


def ensure_unique(apps, schema_editor):
    ClientAccount = apps.get_model("main", "ClientAccount")
    db_alias = schema_editor.connection.alias

    names = defaultdict(int)
    for account in ClientAccount.objects.using(db_alias).all():
        nid = (account.primary_owner_id, account.account_name)
        if nid in names:
            account.account_name += '_{}'.format(names[nid] + 1)
            account.save()
        names[nid] += 1


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_goaltype_risk_factor_weights'),
    ]

    operations = [
        migrations.RunPython(ensure_unique),
        migrations.AlterUniqueTogether(
            name='clientaccount',
            unique_together=set([('primary_owner', 'account_name')]),
        ),
    ]
