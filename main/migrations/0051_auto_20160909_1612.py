# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
from django.utils.functional import curry


def transfer_data(model_name, apps, schema_editor):
    model = apps.get_model("main", model_name)
    db_alias = schema_editor.connection.alias
    for instance in model.objects.using(db_alias).all():
        if instance.residential_address.region.country == 'AU':
            instance.regional_data = {
                'medicare_number': instance.medicare_number,
            }
        instance.clean()
        instance.save()



class Migration(migrations.Migration):

    dependencies = [
        ('main', '0050_firm_fiscal_years'),
    ]

    operations = [
        migrations.AddField(
            model_name='advisor',
            name='regional_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.RunPython(curry(transfer_data, 'Advisor')),
        migrations.AddField(
            model_name='authorisedrepresentative',
            name='regional_data',
            field=jsonfield.fields.JSONField(default=dict),
        ),
        migrations.RunPython(curry(transfer_data, 'AuthorisedRepresentative')),
        migrations.RemoveField(
            model_name='advisor',
            name='medicare_number',
        ),
        migrations.RemoveField(
            model_name='authorisedrepresentative',
            name='medicare_number',
        ),
    ]
