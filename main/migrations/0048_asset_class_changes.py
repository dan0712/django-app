# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators

def copy_id(apps, schema_editor):
    InvestmentType = apps.get_model('main', 'InvestmentType')
    AssetClass = apps.get_model('main', 'AssetClass')
    db_alias = schema_editor.connection.alias
    t_b = InvestmentType.objects.using(db_alias).create(name='BONDS')
    t_s = InvestmentType.objects.using(db_alias).create(name='STOCKS')
    t_m = InvestmentType.objects.using(db_alias).create(name='MIXED')
    for ac in AssetClass.objects.using(db_alias).all():
        if ac.investment_type_int == 'BONDS':
            ac.investment_type_id = t_b.id
        elif ac.investment_type_int == 'STOCKS':
            ac.investment_type_id = t_s.id
        elif ac.investment_type_int == 'MIXED':
            ac.investment_type_id = t_m.id
        else:
            raise Exception("AssetClass {} has no investment type".format(ac.id))
        ac.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_auto_20160829_0942'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid character only accept (0-9a-zA-Z_) ', regex='^[0-9A-Z_]+$')], max_length=255)),
                ('description', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='assetclass',
            name='investment_type',
            field=models.ForeignKey(null=True, to='main.InvestmentType', related_name='asset_classes'),
        ),
        migrations.RunPython(copy_id),
        migrations.AlterField(
            model_name='assetclass',
            name='investment_type',
            field=models.ForeignKey(to='main.InvestmentType', related_name='asset_classes'),
        ),
        migrations.RemoveField(
            model_name='assetclass',
            name='investment_type_int',
        ),
        migrations.RemoveField(
            model_name='assetclass',
            name='super_asset_class',
        ),
    ]
