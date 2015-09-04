# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_auto_20150904_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorisedRepresentative',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('is_accepted', models.BooleanField(default=False, editable=False)),
                ('confirmation_key', models.CharField(null=True, max_length=36, editable=False, blank=True)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('date_of_birth', models.DateField(verbose_name='Date of birth')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=20, default='Male')),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(null=True, blank=True, max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', django_localflavor_au.models.AUStateField(choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')], max_length=3)),
                ('post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('security_question_1', models.CharField(choices=[('What was the name of your elementary school?', 'What was the name of your elementary school?'), ('What was the name of your favorite childhood friend?', 'What was the name of your favorite childhood friend?'), ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')], max_length=255)),
                ('security_question_2', models.CharField(choices=[('What street did you live on in third grade?', 'What street did you live on in third grade?'), ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"), ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')], max_length=255)),
                ('security_answer_1', models.CharField(verbose_name='Answer', max_length=255)),
                ('security_answer_2', models.CharField(verbose_name='Answer', max_length=255)),
                ('medicare_number', models.CharField(max_length=50)),
                ('letter_of_authority', models.FileField(upload_to='')),
                ('betasmartz_agreement', models.BooleanField()),
                ('firm', models.ForeignKey(to='main.Firm', related_name='authorised_representatives')),
                ('user', models.OneToOneField(related_name='authorised_representative', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
