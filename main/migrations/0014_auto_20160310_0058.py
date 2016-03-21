# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def convert_tickers(apps, schema_editor):
    DailyPrice = apps.get_model("main", "DailyPrice")
    MarketCap = apps.get_model("main", "MarketCap")
    Ticker = apps.get_model("main", "Ticker")
    ContentType = apps.get_model("contenttypes", "ContentType")
    ticker_type = ContentType.objects.get_for_model(Ticker)
    db_alias = schema_editor.connection.alias
    for dp in DailyPrice.objects.using(db_alias).all():
        dp.instrument_object_id = dp.ticker_id
        dp.instrument_content_type = ticker_type
        dp.save()
    for mc in MarketCap.objects.using(db_alias).all():
        mc.instrument_object_id = mc.ticker_id
        mc.instrument_content_type = ticker_type
        mc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('main', '0013_auto_20160302_2331'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('display_name', models.CharField(max_length=255, db_index=True)),
                ('description', models.TextField(blank=True, default='')),
                ('url', models.URLField()),
                ('currency', models.CharField(default='AUD', max_length=10)),
                ('data_api', models.CharField(choices=[('portfolios.api.bloomberg', 'Bloomberg')], null=True, max_length=30, help_text='The module that will be used to get the data for this ticker')),
                ('data_api_param', models.CharField(unique=True, null=True, max_length=30, help_text='Structured parameter string appropriate for the data api. The first component would probably be id appropriate for the given api')),
                ('region', models.ForeignKey(to='main.Region')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='MonthlyPrices',
        ),
        migrations.RenameField(
            model_name='dailyprice',
            old_name='nav',
            new_name='price',
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='instrument_content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='instrument_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='marketcap',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='marketcap',
            name='instrument_content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='marketcap',
            name='instrument_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='ticker',
            name='benchmark_content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='ticker',
            name='benchmark_object_id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='marketcap',
            name='value',
            field=models.FloatField(),
        ),
        migrations.AlterUniqueTogether(
            name='dailyprice',
            unique_together=set([('instrument_content_type', 'instrument_object_id', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='marketcap',
            unique_together=set([('instrument_content_type', 'instrument_object_id', 'date')]),
        ),
        migrations.RemoveField(
            model_name='dailyprice',
            name='aum',
        ),
        migrations.RunPython(convert_tickers),
        migrations.RemoveField(
            model_name='dailyprice',
            name='ticker',
        ),
        migrations.RemoveField(
            model_name='marketcap',
            name='ticker',
        ),
    ]
