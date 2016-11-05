# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inflation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('year', models.PositiveIntegerField(help_text="The year the inflation value is for. If after recorded, it is a forecast, otherwise it's an observation.")),
                ('month', models.PositiveIntegerField(help_text="The month the inflation value is for. If after recorded, it is a forecast, otherwise it's an observation.")),
                ('value', models.FloatField(help_text='This is the monthly inflation figure as of the given as_of date.')),
                ('recorded', models.DateField(auto_now=True, help_text='The date this inflation figure was added.')),
            ],
            options={
                'ordering': ['year', 'month'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='inflation',
            unique_together=set([('year', 'month')]),
        ),
    ]
