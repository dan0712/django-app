# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_localflavor_au.models
import main.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20150901_0550'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegalRepresentative',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('is_accepted', models.BooleanField(default=False, editable=False)),
                ('confirmation_key', models.CharField(blank=True, null=True, max_length=36, editable=False)),
                ('is_confirmed', models.BooleanField(default=False, editable=False)),
                ('date_of_birth', models.DateField(verbose_name='Date of birth')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=20, default='Male')),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', django_localflavor_au.models.AUStateField(choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')], max_length=3)),
                ('post_code', django_localflavor_au.models.AUPostCodeField(max_length=4)),
                ('phone_number', django_localflavor_au.models.AUPhoneNumberField(max_length=10)),
                ('security_question_1', models.CharField(choices=[('What was the name of your elementary school?', 'What was the name of your elementary school?'), ('What was the name of your favorite childhood friend?', 'What was the name of your favorite childhood friend?'), ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')], max_length=255)),
                ('security_question_2', models.CharField(choices=[('What street did you live on in third grade?', 'What street did you live on in third grade?'), ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"), ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')], max_length=255)),
                ('security_answer_1', models.CharField(max_length=255, verbose_name='Answer')),
                ('security_answer_2', models.CharField(max_length=255, verbose_name='Answer')),
                ('letter_of_authority', models.FileField(upload_to='')),
                ('betasmartz_agreement', models.BooleanField(validators=[main.models.validate_agreement])),
                ('firm', models.ForeignKey(related_name='legal_representatives', to='main.Firm')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='advisor',
            old_name='work_phone',
            new_name='phone_number',
        ),
        migrations.RenameField(
            model_name='client',
            old_name='accepted',
            new_name='is_accepted',
        ),
        migrations.RemoveField(
            model_name='advisor',
            name='is_supervisor',
        ),
        migrations.AddField(
            model_name='advisor',
            name='address_line_1',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='address_line_2',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='city',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=20, default='Male'),
        ),
        migrations.AddField(
            model_name='advisor',
            name='post_code',
            field=django_localflavor_au.models.AUPostCodeField(max_length=4, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='security_answer_1',
            field=models.CharField(max_length=255, verbose_name='Answer', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='security_answer_2',
            field=models.CharField(max_length=255, verbose_name='Answer', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='security_question_1',
            field=models.CharField(choices=[('What was the name of your elementary school?', 'What was the name of your elementary school?'), ('What was the name of your favorite childhood friend?', 'What was the name of your favorite childhood friend?'), ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')], max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='security_question_2',
            field=models.CharField(choices=[('What street did you live on in third grade?', 'What street did you live on in third grade?'), ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"), ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')], max_length=255, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='advisor',
            name='state',
            field=django_localflavor_au.models.AUStateField(choices=[('ACT', 'Australian Capital Territory'), ('NSW', 'New South Wales'), ('NT', 'Northern Territory'), ('QLD', 'Queensland'), ('SA', 'South Australia'), ('TAS', 'Tasmania'), ('VIC', 'Victoria'), ('WA', 'Western Australia')], max_length=3, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='advisor',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date of birth'),
        ),
        migrations.AlterField(
            model_name='client',
            name='confirmation_key',
            field=models.CharField(blank=True, null=True, max_length=36, editable=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='is_confirmed',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
