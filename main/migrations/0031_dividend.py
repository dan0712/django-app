# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20160115_2005'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dividend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('record_date', models.DateTimeField()),
                ('amount', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], help_text='Amount of the dividend in system currency')),
                ('franking', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)], help_text='Franking percent. 0.01 = 1% of the dividend was franked.')),
                ('instrument', models.ForeignKey(to='main.Ticker')),
            ],
        ),
    ]
