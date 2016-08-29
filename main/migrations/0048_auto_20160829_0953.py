# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0047_auto_20160829_0942'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator(message='Invalid character only accept (0-9a-zA-Z_) ', regex='^[0-9A-Z_]+$')], max_length=255)),
                ('description', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='assetclass',
            name='investment_type',
            field=models.ForeignKey(default=1, to='main.InvestmentType', related_name='asset_classes'),
            preserve_default=False,
        ),
    ]
