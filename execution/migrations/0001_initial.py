# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('ResponseCode', models.IntegerField()),
                ('Result', jsonfield.fields.JSONField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ETNALogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('ResponseCode', models.IntegerField(db_index=True)),
                ('Ticket', models.CharField(max_length=521)),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LoginResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('SessionId', models.CharField(max_length=128)),
                ('UserId', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SecurityETNA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('symbol_id', models.IntegerField()),
                ('Symbol', models.CharField(max_length=128)),
                ('Description', models.CharField(max_length=128)),
                ('Currency', models.CharField(max_length=20)),
                ('Price', models.FloatField()),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='etnalogin',
            name='Result',
            field=models.OneToOneField(to='execution.LoginResult', related_name='ETNALogin'),
        ),
    ]
