# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('address', models.TextField(help_text='The full address excluding country, first level administrative region (state/province etc) and postcode')),
                ('post_code', models.CharField(max_length=16, blank=True, null=True)),
                ('global_id', models.CharField(null=True, max_length=64, blank=True, help_text='Global identifier of the address in whatever API we are using (if any)')),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('code', models.CharField(null=True, max_length=16, blank=True, db_index=True)),
                ('country', models.CharField(max_length=2)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('country', 'name')]),
        ),
        migrations.AddField(
            model_name='address',
            name='region',
            field=models.ForeignKey(related_name='+', to='address.Region'),
        ),
    ]
