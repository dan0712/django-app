# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def delete_old(apps, schema_editor):
    schema_editor.delete_model(apps.get_model('main', 'ProxyAssetClass'))
    schema_editor.delete_model(apps.get_model('main', 'ProxyTicker'))
    schema_editor.delete_model(apps.get_model('main', 'PortfolioSet'))
    schema_editor.delete_model(apps.get_model('main', 'View'))
    schema_editor.delete_model(apps.get_model('main', 'MarketCap'))


# Before running this migration, you need to stop the app and drop the corresponding main tables.
class Migration(migrations.Migration):

    dependencies = [
        ('main', '0051_auto_20160219_0657'),
        ('portfolios', '0008_auto_20151230_2024'),
    ]

    database_operations = [
        migrations.AlterModelTable('ProxyAssetClass', 'main_proxyassetclass'),
        migrations.AlterModelTable('ProxyTicker', 'main_proxyticker'),
        migrations.AlterModelTable('PortfolioSet', 'main_portfolioset'),
        migrations.AlterModelTable('View', 'main_view'),
        migrations.AlterModelTable('MarketCap', 'main_marketcap'),
    ]

    state_operations = [
        migrations.DeleteModel('ProxyAssetClass'),
        migrations.DeleteModel('ProxyTicker'),
        migrations.DeleteModel('PortfolioSet'),
        migrations.DeleteModel('View'),
        migrations.DeleteModel('MarketCap'),
    ]

    operations = [
        migrations.RunPython(delete_old),
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
