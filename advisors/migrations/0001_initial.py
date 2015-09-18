# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0057_auto_20150918_2000'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkInvestorTransfer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('signature', models.FileField(upload_to='')),
                ('bulk_investors_spreadsheet', models.ManyToManyField(to='main.Client')),
                ('from_advisor', models.ForeignKey(to='main.Advisor')),
                ('to_advisor', models.ForeignKey(related_name='bulk_transfer_to_advisors', to='main.Advisor')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeDealerGroup',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(null=True)),
                ('office_address_line_1', models.CharField(max_length=255, verbose_name='Office address 1')),
                ('office_address_line_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Office address 2')),
                ('office_state', django_localflavor_au.models.AUStateField(choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')], max_length=3)),
                ('office_city', models.CharField(max_length=255)),
                ('office_post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('postal_address_line_1', models.CharField(max_length=255, verbose_name='Postal address 1')),
                ('postal_address_line_2', models.CharField(blank=True, max_length=255, null=True, verbose_name='Postal address 2')),
                ('postal_state', django_localflavor_au.models.AUStateField(choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')], max_length=3)),
                ('same_address', models.BooleanField(default=False)),
                ('postal_city', models.CharField(max_length=255)),
                ('postal_post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('daytime_phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('mobile_phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('fax_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('alternate_email_address', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email address')),
                ('letter_previous_group', models.FileField(upload_to='')),
                ('letter_new_group', models.FileField(upload_to='')),
                ('signature', models.FileField(upload_to='')),
                ('advisor', models.ForeignKey(to='main.Advisor')),
                ('bulk_investors_spreadsheet', models.ManyToManyField(to='main.Client')),
                ('new_firm', models.ForeignKey(related_name='new_advisors', to='main.Firm')),
                ('old_firm', models.ForeignKey(related_name='old_advisors', to='main.Firm')),
            ],
        ),
        migrations.CreateModel(
            name='SingleInvestorTransfer',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('signature_investor', models.FileField(upload_to='')),
                ('signature_advisor', models.FileField(upload_to='')),
                ('signature_joint_investor', models.FileField(upload_to='')),
                ('from_advisor', models.ForeignKey(to='main.Advisor')),
                ('investors', models.ForeignKey(to='main.Client')),
                ('to_advisor', models.ForeignKey(related_name='single_transfer_to_advisors', to='main.Advisor')),
            ],
        ),
    ]
