# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20150903_0350'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('advisor', models.ForeignKey(to='main.Advisor', related_name='primary_account_groups')),
                ('secondary_advisors', models.ManyToManyField(to='main.Advisor', related_name='secondary_account_groups')),
            ],
        ),
        migrations.CreateModel(
            name='ClientAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('custom_fee', models.PositiveIntegerField()),
                ('account_type', models.PositiveIntegerField(default=1, choices=[(1, 'Personal Account')])),
                ('account_group', models.ForeignKey(to='main.AccountGroup', related_name='accounts')),
            ],
        ),
        migrations.AddField(
            model_name='client',
            name='secondary_advisors',
            field=models.ManyToManyField(to='main.Advisor', related_name='secondary_clients'),
        ),
        migrations.AddField(
            model_name='clientaccount',
            name='primary_owner',
            field=models.ForeignKey(to='main.Client', related_name='accounts'),
        ),
    ]
