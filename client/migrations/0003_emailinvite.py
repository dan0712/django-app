# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_auto_20160824_1515'),
        ('client', '0002_emailnotificationprefs'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailInvite',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('last_sent_at', models.DateTimeField(blank=True, null=True)),
                ('send_count', models.PositiveIntegerField(default=0)),
                ('reason', models.PositiveIntegerField(choices=[(1, 'Retirement'), (2, 'Personal Investing')], blank=True, null=True)),
                ('status', models.PositiveIntegerField(choices=[(0, 'Created'), (1, 'Sent'), (2, 'Accepted'), (4, 'Closed')], default=0)),
                ('advisor', models.ForeignKey(related_name='invites', to='main.Advisor')),
            ],
        ),
    ]
