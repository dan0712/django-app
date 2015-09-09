# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_auto_20150909_1554'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('value', models.FloatField(verbose_name=0)),
                ('goal', models.ForeignKey(to='main.Goal', related_name='positions')),
            ],
        ),
        migrations.AlterField(
            model_name='ticker',
            name='unit_price',
            field=models.FloatField(default=10),
        ),
        migrations.AddField(
            model_name='position',
            name='ticker',
            field=models.ForeignKey(to='main.Ticker'),
        ),
    ]
