# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0003_auto_20160111_0208'),
        ('retiresmartz', '0004_auto_20160926_2230'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetirementAdvice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('dt', models.DateTimeField(auto_now_add=True)),
                ('read', models.DateTimeField(blank=True, null=True)),
                ('text', models.CharField(max_length=512)),
                ('action', models.CharField(blank=True, max_length=12)),
                ('action_url', models.CharField(blank=True, max_length=512)),
                ('action_data', models.CharField(blank=True, max_length=512)),
                ('plan', models.ForeignKey(related_name='advice', to='retiresmartz.RetirementPlan')),
                ('trigger', models.ForeignKey(related_name='advice', to='eventlog.Log')),
            ],
        ),
    ]
