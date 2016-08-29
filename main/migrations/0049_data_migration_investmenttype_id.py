# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models


def copy_id(apps, schema_editor):
    InvestmentType = apps.get_model('main', 'InvestmentType')
    AssetClass = apps.get_model('main', 'AssetClass')
    db_alias = schema_editor.connection.alias
    InvestmentType.objects.using(db_alias).create(name='BONDS')
    InvestmentType.objects.using(db_alias).create(name='STOCKS')
    InvestmentType.objects.using(db_alias).create(name='MIXED')
    for ac in AssetClass.objects.using(db_alias).all():
        if ac.investment_type_int == 'BONDS':
            ac.investment_type_id = 1
        elif ac.investment_type_int == 'STOCKS':
            ac.investment_type_id = 2
        elif ac.investment_type_int == 'MIXED':
            ac.investment_type_id = 3
        ac.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0048_auto_20160829_0953'),
    ]

    operations = [
        migrations.RunPython(copy_id),
    ]
