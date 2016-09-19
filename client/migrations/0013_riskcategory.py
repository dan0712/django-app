# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0012_auto_20160917_0449'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('upper_bound', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('name', models.CharField(max_length=128)),
            ],
        ),
    ]
