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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('ResponseCode', models.IntegerField()),
                ('Result', jsonfield.fields.JSONField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ETNALogin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('ResponseCode', models.IntegerField()),
                ('Ticket', models.CharField(max_length=521)),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LoginResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('SessionId', models.CharField(max_length=128)),
                ('UserId', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='OrderETNA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('Price', models.FloatField()),
                ('Exchange', models.CharField(max_length=128, default='Auto')),
                ('TrailingLimitAmount', models.FloatField(default=0)),
                ('AllOrNone', models.IntegerField(default=0)),
                ('TrailingStopAmount', models.FloatField(default=0)),
                ('Type', models.IntegerField(default=1, choices=[(0, 'Market'), (1, 'Limit')])),
                ('Quantity', models.IntegerField()),
                ('SecurityId', models.IntegerField()),
                ('Side', models.IntegerField(choices=[(0, 'Buy'), (1, 'Sell')])),
                ('TimeInForce', models.IntegerField(default=6, choices=[(0, 'Day'), (1, 'GoodTillCancel'), (2, 'AtTheOpening'), (3, 'ImmediateOrCancel'), (4, 'FillOrKill'), (5, 'GoodTillCrossing'), (6, 'GoodTillDate')])),
                ('StopPrice', models.FloatField(default=0)),
                ('ExpireDate', models.IntegerField()),
                ('created', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('Order_Id', models.IntegerField(default=-1)),
                ('Status', models.CharField(max_length=128, default='New', choices=[('New', 'New'), ('Sent', 'Sent'), ('PartiallyFilled', 'PartiallyFilled'), ('Filled', 'Filled'), ('DoneForDay', 'DoneForDay'), ('Canceled', 'Canceled'), ('Replaced', 'Replaced'), ('PendingCancel', 'PendingCancel'), ('Stopped', 'Stopped'), ('Rejected', 'Rejected'), ('Suspended', 'Suspended'), ('PendingNew', 'PendingNew'), ('Calculated', 'Calculated'), ('Expired', 'Expired'), ('AcceptedForBidding', 'AcceptedForBidding'), ('PendingReplace', 'PendingReplace'), ('Error', 'Error')], db_index=True)),
                ('FillPrice', models.FloatField(default=0)),
                ('FillQuantity', models.IntegerField(default=0)),
                ('Description', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='SecurityETNA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
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
            field=models.OneToOneField(related_name='ETNALogin', to='execution.LoginResult'),
        ),
    ]
