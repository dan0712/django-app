# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BulkInvestorTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('signature', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeDealerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('approved', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(null=True)),
                ('work_phone', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('letter_previous_group', models.FileField(upload_to='')),
                ('letter_new_group', models.FileField(upload_to='')),
                ('signature', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='SingleInvestorTransfer',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('approved', models.BooleanField(default=False)),
                ('approved_at', models.DateTimeField(null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('signature_investor', models.FileField(upload_to='')),
                ('signature_advisor', models.FileField(upload_to='')),
                ('signature_joint_investor', models.FileField(upload_to='')),
            ],
        ),
    ]
