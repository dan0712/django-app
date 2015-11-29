# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0013_auto_20151108_0424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisor',
            name='security_question_1',
            field=models.CharField(default='', max_length=255, choices=[
                ('What was the name of your primary school?', 'What was the name of your primary school?'),
                ("What is your mother's maiden name?", "What is your mother's maiden name?"),
                ('What was the name of your first pet?', 'What was the name of your first pet?')]),
        ),
        migrations.AlterField(
            model_name='advisor',
            name='security_question_2',
            field=models.CharField(default='', max_length=255,
                                   choices=[('What was your first car?', 'What was your first car?'), (
                                   'What was your favorite subject at school?',
                                   'What was your favorite subject at school?'), ('In what month was your father born?',
                                                                                  'In what month was your father born?')]),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_question_1',
            field=models.CharField(default='', max_length=255, choices=[
                ('What was the name of your primary school?', 'What was the name of your primary school?'),
                ("What is your mother's maiden name?", "What is your mother's maiden name?"),
                ('What was the name of your first pet?', 'What was the name of your first pet?')]),
        ),
        migrations.AlterField(
            model_name='authorisedrepresentative',
            name='security_question_2',
            field=models.CharField(default='', max_length=255,
                                   choices=[('What was your first car?', 'What was your first car?'), (
                                   'What was your favorite subject at school?',
                                   'What was your favorite subject at school?'), ('In what month was your father born?',
                                                                                  'In what month was your father born?')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_question_1',
            field=models.CharField(default='', max_length=255, choices=[
                ('What was the name of your primary school?', 'What was the name of your primary school?'),
                ("What is your mother's maiden name?", "What is your mother's maiden name?"),
                ('What was the name of your first pet?', 'What was the name of your first pet?')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='security_question_2',
            field=models.CharField(default='', max_length=255,
                                   choices=[('What was your first car?', 'What was your first car?'), (
                                   'What was your favorite subject at school?',
                                   'What was your favorite subject at school?'), ('In what month was your father born?',
                                                                                  'In what month was your father born?')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='tax_file_number',
            field=models.CharField(max_length=9, null=True, blank=True),
        ),
    ]
