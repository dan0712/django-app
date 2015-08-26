# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import main.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('is_confirmed', models.BooleanField()),
                ('confirmation_key', models.CharField(max_length=36)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AssetClass',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid character only accept (0-9a-zA-Z_) ', regex='^[0-9a-zA-Z_]+$')], max_length=255)),
                ('display_order', models.PositiveIntegerField()),
                ('primary_color', main.fields.ColorField(max_length=10)),
                ('foreground_color', main.fields.ColorField(max_length=10)),
                ('drift_color', main.fields.ColorField(max_length=10)),
                ('asset_class_explanation', models.TextField(default='', blank=True)),
                ('tickers_explanation', models.TextField(default='', blank=True)),
                ('display_name', models.CharField(max_length=255)),
                ('investment_type', models.CharField(choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS')], max_length=255)),
                ('super_asset_class', models.CharField(choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('is_confirmed', models.BooleanField()),
                ('confirmation_key', models.CharField(max_length=36)),
                ('advisor', models.ForeignKey(to='main.Advisor')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticker',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid symbol format', regex='^[^ ]+$')], max_length=10)),
                ('display_name', models.CharField(max_length=255)),
                ('description', models.TextField(default='', blank=True)),
                ('ordering', models.IntegerField(default='', blank=True)),
                ('url', models.URLField()),
                ('unit_price', models.FloatField(default=1, editable=False)),
                ('asset_class', models.ForeignKey(related_name='tickers', to='main.AssetClass')),
            ],
        ),
    ]
