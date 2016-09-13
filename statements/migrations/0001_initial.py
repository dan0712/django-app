# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0007_auto_20160908_0307'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordOfAdvice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(related_name='records_of_advice', to='client.ClientAccount')),
            ],
            options={
                'ordering': ('-create_date',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StatementOfAdvice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('account', models.OneToOneField(to='client.ClientAccount', related_name='statement_of_advice')),
            ],
            options={
                'ordering': ('-create_date',),
                'abstract': False,
            },
        ),
    ]
