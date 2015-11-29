# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_localflavor_au.models
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0006_user_prepopulated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='address_line_1',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='city',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date of birth', null=True),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='medicare_number',
            field=models.CharField(max_length=50, default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='phone_number',
            field=django_localflavor_au.models.AUPhoneNumberField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='post_code',
            field=django_localflavor_au.models.AUPostCodeField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='security_answer_1',
            field=models.CharField(verbose_name='Answer', max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='security_answer_2',
            field=models.CharField(verbose_name='Answer', max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='security_question_1',
            field=models.CharField(max_length=255, choices=[
                ('What was the name of your elementary school?', 'What was the name of your elementary school?'), (
                'What was the name of your favorite childhood friend?',
                'What was the name of your favorite childhood friend?'),
                ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')], default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='security_question_2',
            field=models.CharField(max_length=255, choices=[
                ('What street did you live on in third grade?', 'What street did you live on in third grade?'),
                ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"),
                ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')],
                                   default=''),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='state',
            field=django_localflavor_au.models.AUStateField(max_length=3,
                                                            choices=[('ACT', 'Australian Capital Territory'),
                                                                     ('NSW', 'New South Wales'),
                                                                     ('NT', 'Northern Territory'),
                                                                     ('QLD', 'Queensland'), ('SA', 'South Australia'),
                                                                     ('TAS', 'Tasmania'), ('VIC', 'Victoria'),
                                                                     ('WA', 'Western Australia')], default='QLD'),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='address_line_1',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='city',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date of birth', null=True),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='medicare_number',
            field=models.CharField(max_length=50, default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='phone_number',
            field=django_localflavor_au.models.AUPhoneNumberField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='post_code',
            field=django_localflavor_au.models.AUPostCodeField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_answer_1',
            field=models.CharField(verbose_name='Answer', max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_answer_2',
            field=models.CharField(verbose_name='Answer', max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_question_1',
            field=models.CharField(max_length=255, choices=[
                ('What was the name of your elementary school?', 'What was the name of your elementary school?'), (
                'What was the name of your favorite childhood friend?',
                'What was the name of your favorite childhood friend?'),
                ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')], default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_question_2',
            field=models.CharField(max_length=255, choices=[
                ('What street did you live on in third grade?', 'What street did you live on in third grade?'),
                ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"),
                ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')],
                                   default=''),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='state',
            field=django_localflavor_au.models.AUStateField(max_length=3,
                                                            choices=[('ACT', 'Australian Capital Territory'),
                                                                     ('NSW', 'New South Wales'),
                                                                     ('NT', 'Northern Territory'),
                                                                     ('QLD', 'Queensland'), ('SA', 'South Australia'),
                                                                     ('TAS', 'Tasmania'), ('VIC', 'Victoria'),
                                                                     ('WA', 'Western Australia')], default='QLD'),
        ),
        migrations.AlterField(
            model_name='client',
            name='address_line_1',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='advisor_agreement',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='betasmartz_agreement',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='city',
            field=models.CharField(max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='date_of_birth',
            field=models.DateField(verbose_name='Date of birth', null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='medicare_number',
            field=models.CharField(max_length=50, default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone_number',
            field=django_localflavor_au.models.AUPhoneNumberField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='post_code',
            field=django_localflavor_au.models.AUPostCodeField(max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_answer_1',
            field=models.CharField(verbose_name='Answer', max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_answer_2',
            field=models.CharField(verbose_name='Answer', max_length=255, default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_question_1',
            field=models.CharField(max_length=255, choices=[
                ('What was the name of your elementary school?', 'What was the name of your elementary school?'), (
                'What was the name of your favorite childhood friend?',
                'What was the name of your favorite childhood friend?'),
                ('What was the name of your childhood pet?', 'What was the name of your childhood pet?')], default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_question_2',
            field=models.CharField(max_length=255, choices=[
                ('What street did you live on in third grade?', 'What street did you live on in third grade?'),
                ("What is your oldest sibling's birth month?", "What is your oldest sibling's birth month?"),
                ('In what city did your mother and father meet?', 'In what city did your mother and father meet?')],
                                   default=''),
        ),
        migrations.AlterField(
            model_name='client',
            name='state',
            field=django_localflavor_au.models.AUStateField(max_length=3,
                                                            choices=[('ACT', 'Australian Capital Territory'),
                                                                     ('NSW', 'New South Wales'),
                                                                     ('NT', 'Northern Territory'),
                                                                     ('QLD', 'Queensland'), ('SA', 'South Australia'),
                                                                     ('TAS', 'Tasmania'), ('VIC', 'Victoria'),
                                                                     ('WA', 'Western Australia')], default='QLD'),
        ),
    ]
