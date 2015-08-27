# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.auth.models
import django.utils.timezone
import django.core.validators
import main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(verbose_name='first name', max_length=30)),
                ('middle_name', models.CharField(verbose_name='middle name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', max_length=30)),
                ('username', models.CharField(default='', editable=False, max_length=30)),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, unique=True, verbose_name='email address', max_length=254)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(to='auth.Group', verbose_name='groups', related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', verbose_name='user permissions', related_query_name='user', help_text='Specific permissions for this user.', related_name='user_set', blank=True)),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('is_confirmed', models.BooleanField(editable=False, default=False)),
                ('confirmation_key', models.CharField(max_length=36)),
                ('work_phone', models.PositiveIntegerField()),
                ('token', models.CharField(editable=False, null=True, max_length=36)),
                ('accepted', models.BooleanField(editable=False, default=False)),
                ('date_of_birth', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='AssetClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid character only accept (0-9a-zA-Z_) ', regex='^[0-9a-zA-Z_]+$')], max_length=255)),
                ('display_order', models.PositiveIntegerField()),
                ('primary_color', main.fields.ColorField(max_length=10)),
                ('foreground_color', main.fields.ColorField(max_length=10)),
                ('drift_color', main.fields.ColorField(max_length=10)),
                ('asset_class_explanation', models.TextField(default='', blank=True)),
                ('tickers_explanation', models.TextField(default='', blank=True)),
                ('display_name', models.CharField(max_length=255)),
                ('investment_type', models.CharField(choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS')], max_length=255)),
                ('super_asset_class', models.CharField(choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('Equity_INT', 'Equity_INT'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('is_confirmed', models.BooleanField()),
                ('confirmation_key', models.CharField(max_length=36)),
                ('accepted', models.BooleanField(editable=False, default=False)),
                ('date_of_birth', models.DateField()),
                ('advisor', models.ForeignKey(to='main.Advisor')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Firm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('firm_name', models.CharField(max_length=255)),
                ('firm_slug', models.CharField(editable=False, unique=True, max_length=255)),
                ('firm_logo_url', models.ImageField(upload_to='')),
                ('firm_knocked_out_logo_url', models.ImageField(upload_to='')),
                ('firm_client_agreement_url', models.FileField(blank=True, null=True, upload_to='')),
                ('firm_form_adv_part2_url', models.FileField(blank=True, null=True, upload_to='')),
                ('firm_client_agreement_token', models.CharField(editable=False, max_length=36)),
            ],
        ),
        migrations.CreateModel(
            name='Ticker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('symbol', models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid symbol format', regex='^[^ ]+$')], max_length=10)),
                ('display_name', models.CharField(max_length=255)),
                ('description', models.TextField(default='', blank=True)),
                ('ordering', models.IntegerField(default='', blank=True)),
                ('url', models.URLField()),
                ('unit_price', models.FloatField(editable=False, default=1)),
                ('asset_class', models.ForeignKey(to='main.AssetClass', related_name='tickers')),
            ],
        ),
        migrations.AddField(
            model_name='advisor',
            name='firm',
            field=models.ForeignKey(to='main.Firm'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
