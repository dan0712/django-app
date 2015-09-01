# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings
import django.utils.timezone
import django_localflavor_au.models
import django.contrib.auth.models
import main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('middle_name', models.CharField(max_length=30, blank=True, verbose_name='middle name')),
                ('last_name', models.CharField(max_length=30, verbose_name='last name')),
                ('username', models.CharField(max_length=30, editable=False, default='')),
                ('email', models.EmailField(max_length=254, unique=True, error_messages={'unique': 'A user with that email already exists.'}, verbose_name='email address')),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, related_name='user_set', to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='user_set', to='auth.Permission', help_text='Specific permissions for this user.', verbose_name='user permissions', related_query_name='user')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Advisor',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('work_phone', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('confirmation_key', models.CharField(max_length=36, blank=True, null=True, editable=False)),
                ('token', models.CharField(max_length=36, null=True, editable=False)),
                ('is_accepted', models.BooleanField(editable=False, default=False)),
                ('is_confirmed', models.BooleanField(editable=False, default=False)),
                ('date_of_birth', models.DateField()),
                ('is_supervisor', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AssetClass',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(regex='^[0-9a-zA-Z_]+$', message='Invalid character only accept (0-9a-zA-Z_) ')])),
                ('display_order', models.PositiveIntegerField()),
                ('primary_color', main.fields.ColorField(max_length=10)),
                ('foreground_color', main.fields.ColorField(max_length=10)),
                ('drift_color', main.fields.ColorField(max_length=10)),
                ('asset_class_explanation', models.TextField(blank=True, default='')),
                ('tickers_explanation', models.TextField(blank=True, default='')),
                ('display_name', models.CharField(max_length=255)),
                ('investment_type', models.CharField(max_length=255, choices=[('BONDS', 'BONDS'), ('STOCKS', 'STOCKS')])),
                ('super_asset_class', models.CharField(max_length=255, choices=[('EQUITY_AU', 'EQUITY_AU'), ('EQUITY_US', 'EQUITY_US'), ('EQUITY_EU', 'EQUITY_EU'), ('EQUITY_EM', 'EQUITY_EM'), ('EQUITY_INT', 'EQUITY_INT'), ('FIXED_INCOME_AU', 'FIXED_INCOME_AU'), ('FIXED_INCOME_US', 'FIXED_INCOME_US'), ('FIXED_INCOME_EU', 'FIXED_INCOME_EU'), ('FIXED_INCOME_EM', 'FIXED_INCOME_EM'), ('FIXED_INCOME_INT', 'FIXED_INCOME_INT')])),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('is_confirmed', models.BooleanField()),
                ('confirmation_key', models.CharField(max_length=36)),
                ('accepted', models.BooleanField(editable=False, default=False)),
                ('date_of_birth', models.DateField(verbose_name='Date of birth')),
                ('gender', models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', django_localflavor_au.models.AUStateField(max_length=3, choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')])),
                ('post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('medicare_number', models.CharField(max_length=50)),
                ('tax_file_number', models.CharField(max_length=50)),
                ('provide_tfn', models.IntegerField(choices=[(0, 'Yes'), (1, 'I am a non-resident of Australia'), (2, 'I want to claim an exemption'), (3, 'I do not want to quote a Tax File Number or exemption')], default=0, verbose_name='Provide TFN?')),
                ('security_question_1', models.CharField(max_length=255, choices=[('What was the name of your elementary school?', 'What was the name of your elementary school?'), ('What was the name of your favorite childhood friend?', 'What was the name of your favorite childhood friend?'), ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')])),
                ('security_question_2', models.CharField(max_length=255, choices=[('What street did you live on in third grade?', 'What street did you live on in third grade?'), ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"), ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')])),
                ('security_answer_1', models.CharField(max_length=255, verbose_name='Answer')),
                ('security_answer_2', models.CharField(max_length=255, verbose_name='Answer')),
                ('associated_to_broker_dealer', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='You are employed by or associated with a broker dealer.')),
                ('ten_percent_insider', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False, verbose_name='You are a 10% shareholder, director, or policy maker of a publicly traded company.')),
                ('advisor', models.ForeignKey(to='main.Advisor')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClientInvite',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('client_email', models.EmailField(max_length=254, unique=True)),
                ('sent_date', models.DateTimeField(auto_now=True)),
                ('is_user', models.BooleanField(default=False)),
                ('advisor', models.ForeignKey(to='main.Advisor', related_name='client_invites')),
            ],
        ),
        migrations.CreateModel(
            name='Firm',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('dealer_group_number', models.CharField(max_length=50, default='')),
                ('slug', models.CharField(max_length=255, unique=True, editable=False)),
                ('logo_url', models.ImageField(upload_to='', verbose_name='White logo')),
                ('knocked_out_logo_url', models.ImageField(upload_to='', verbose_name='Colored logo')),
                ('client_agreement_url', models.FileField(upload_to='', blank=True, null=True, verbose_name='Client Agreement (PDF)')),
                ('form_adv_part2_url', models.FileField(upload_to='', blank=True, null=True, verbose_name='Form Adv')),
                ('token', models.CharField(max_length=36, editable=False)),
                ('fee', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='FirmData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('afsl_asic', models.CharField(max_length=50, default='')),
                ('afsl_asic_document', models.FileField(upload_to='')),
                ('office_address_line_1', models.CharField(max_length=255)),
                ('office_address_line_2', models.CharField(max_length=255)),
                ('office_state', django_localflavor_au.models.AUStateField(max_length=3, choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')])),
                ('office_city', models.CharField(max_length=255)),
                ('office_post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('postal_address_line_1', models.CharField(max_length=255)),
                ('postal_address_line_2', models.CharField(max_length=255)),
                ('postal_state', django_localflavor_au.models.AUStateField(max_length=3, choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')])),
                ('postal_city', models.CharField(max_length=255)),
                ('postal_post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('daytime_phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('mobile_phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('fax_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('alternate_email_address', models.EmailField(max_length=254, blank=True, null=True)),
                ('last_change', models.DateField(auto_now=True)),
                ('fee_bank_account_name', models.CharField(max_length=100)),
                ('fee_bank_account_branch_name', models.CharField(max_length=100)),
                ('fee_bank_account_bsb_number', models.CharField(max_length=20)),
                ('fee_bank_account_number', models.CharField(max_length=20)),
                ('fee_bank_account_holder_name', models.CharField(max_length=100)),
                ('australian_business_number', models.CharField(max_length=20)),
                ('investor_transfer', models.BooleanField(choices=[(False, 'No'), (True, 'Yes')], default=False)),
                ('previous_adviser_name', models.CharField(max_length=100, blank=True, null=True)),
                ('previous_margin_lending_adviser_number', models.CharField(max_length=100, blank=True, null=True)),
                ('previous_bt_adviser_number', models.CharField(max_length=100, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ticker',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(regex='^[^ ]+$', message='Invalid symbol format')])),
                ('display_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('ordering', models.IntegerField(blank=True, default='')),
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
            field=models.OneToOneField(related_name='advisor', to=settings.AUTH_USER_MODEL),
        ),
    ]
