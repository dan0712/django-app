# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('confirmation_key', models.CharField(max_length=36)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AssetClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('display_order', models.IntegerField()),
                ('donut_order', models.IntegerField()),
                ('primary_color', main.fields.ColorField(max_length=10)),
                ('foreground_color', main.fields.ColorField(max_length=10)),
                ('drift_color', main.fields.ColorField(max_length=10)),
                ('asset_class_explanation', models.TextField()),
                ('tickers_explanation', models.TextField()),
                ('display_name', models.CharField(max_length=255)),
                ('investment_type', models.CharField(choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS')], max_length=255)),
                ('super_asset_class', models.CharField(choices=[('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EM', 'EQUITY_EM'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM')], max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Asset classes',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('confirmation_key', models.CharField(max_length=36)),
                ('advisor', models.ForeignKey(to='main.Advisor', related_name='clients')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('symbol', models.CharField(max_length=255)),
                ('display_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('ordering', models.IntegerField()),
                ('url', models.URLField()),
                ('unit_price', models.FloatField()),
                ('primary', models.BooleanField(default=False)),
                ('asset_classes', models.ManyToManyField(blank=True, to='main.AssetClass', related_name='tickers')),
            ],
        ),
    ]
