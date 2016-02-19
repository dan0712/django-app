# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkInvestorTransfer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('signatures', models.FileField(upload_to='')),
                ('firm', models.ForeignKey(to='main.Firm', editable=False)),
                ('from_advisor', models.ForeignKey(to='main.Advisor')),
                ('investors', models.ManyToManyField(to='main.Client')),
                ('to_advisor', models.ForeignKey(to='main.Advisor', verbose_name='To Advisor', related_name='bulk_transfer_to_advisors')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeDealerGroup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(null=True, blank=True)),
                ('work_phone', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('new_email', models.EmailField(max_length=254)),
                ('letter_previous_group', models.FileField(upload_to='', verbose_name='Prev. Group Letter')),
                ('letter_new_group', models.FileField(upload_to='', verbose_name='New Group Letter')),
                ('signature', models.FileField(upload_to='')),
                ('advisor', models.ForeignKey(to='main.Advisor')),
                ('new_firm', models.ForeignKey(to='main.Firm', related_name='new_advisors')),
                ('old_firm', models.ForeignKey(to='main.Firm', related_name='old_advisors')),
            ],
        ),
        migrations.CreateModel(
            name='SingleInvestorTransfer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('signatures', models.FileField(upload_to='')),
                ('firm', models.ForeignKey(to='main.Firm', editable=False)),
                ('from_advisor', models.ForeignKey(to='main.Advisor')),
                ('investor', models.ForeignKey(to='main.Client')),
                ('to_advisor', models.ForeignKey(to='main.Advisor', verbose_name='To Advisor', related_name='single_transfer_to_advisors')),
            ],
        ),
    ]
