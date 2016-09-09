# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


def transfer_data(apps, schema_editor):
    Client = apps.get_model("client", "Client")
    db_alias = schema_editor.connection.alias
    for client in Client.objects.using(db_alias).all():
        if client.residential_address.region.country == 'US':
            client.regional_data = {
                'associated_to_broker_dealer': bool(client.associated_to_broker_dealer),
                'public_position_insider': bool(client.public_position_insider),
                'ten_percent_insider': bool(client.ten_percent_insider),
                'us_citizen': bool(client.us_citizen),
            }
        else:
            client.regional_data = {
                'tax_file_number': client.tax_file_number,
                'provide_tfn': bool(client.provide_tfn),
                'medicare_number': client.medicare_number,
            }
        client.clean()
        client.save()


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0006_auto_20160906_0039'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='regional_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.RunPython(transfer_data),
        migrations.RemoveField(
            model_name='client',
            name='associated_to_broker_dealer',
        ),
        migrations.RemoveField(
            model_name='client',
            name='medicare_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='provide_tfn',
        ),
        migrations.RemoveField(
            model_name='client',
            name='public_position_insider',
        ),
        migrations.RemoveField(
            model_name='client',
            name='tax_file_number',
        ),
        migrations.RemoveField(
            model_name='client',
            name='ten_percent_insider',
        ),
        migrations.RemoveField(
            model_name='client',
            name='us_citizen',
        ),
    ]
