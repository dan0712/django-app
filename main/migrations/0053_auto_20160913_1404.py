# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_auto_20160910_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalInstrument',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('institution', models.IntegerField(choices=[(0, 'APEX'), (1, 'INTERACTIVE_BROKERS')], default=0)),
                ('instrument_id', models.CharField(max_length=10)),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='external_instruments', to='main.Ticker')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='externalinstrument',
            unique_together=set([('institution', 'instrument_id'), ('institution', 'ticker')]),
        ),
    ]
