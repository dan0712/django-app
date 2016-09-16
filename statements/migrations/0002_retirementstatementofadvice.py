# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retiresmartz', '0001_initial'),
        ('statements', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetirementStatementOfAdvice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('retirement_plan', models.OneToOneField(to='retiresmartz.RetirementPlan', related_name='statement_of_advice')),
            ],
            options={
                'abstract': False,
                'ordering': ('-create_date',),
            },
        ),
    ]
