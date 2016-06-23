# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0003_auto_20160111_0208'),
        ('main', '0036_auto_20160609_2205'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventMemo',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('staff', models.BooleanField(help_text='Staff memos can only be seen by staff members of the firm. Non-Staff memos inherit the permissions of the logged event. I.e. Whoever can see the event, can see the memo.')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='memos', to='eventlog.Log')),
            ],
        ),
        migrations.RemoveField(
            model_name='transactionmemo',
            name='transaction',
        ),
        migrations.DeleteModel(
            name='TransactionMemo',
        ),
    ]
