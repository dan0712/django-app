# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from main.constants import ACCOUNT_TYPES


def create_new_account_types(apps, schema_editor):
    AccountType = apps.get_model("main", "AccountType")
    db_alias = schema_editor.connection.alias

    for ac_id, _ in ACCOUNT_TYPES:
        AccountType.objects.using(db_alias).get_or_create(pk=ac_id)


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0070_auto_20161118_0648'),
    ]

    operations = [
        migrations.RunPython(create_new_account_types)
    ]
