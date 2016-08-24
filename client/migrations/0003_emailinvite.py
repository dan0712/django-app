# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_auto_20160821_0150'),
        ('client', '0002_emailnotificationprefs'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailInvite',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('last_sent_date', models.DateTimeField(blank=True, null=True)),
                ('send_count', models.PositiveIntegerField(default=0)),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Created'), (1, 'Sent'), (2, 'Accepted'), (4, 'Closed')])),
                ('advisor', models.ForeignKey(to='main.Advisor', related_name='invites')),
            ],
        ),
    ]
