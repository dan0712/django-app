# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0069_auto_20161110_0645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apexfill',
            name='apex_order',
        ),
        migrations.RemoveField(
            model_name='marketorderrequestapex',
            name='apex_order',
        ),
        migrations.AlterField(
            model_name='orderetna',
            name='Status',
            field=models.CharField(max_length=128, choices=[('New', 'New'), ('Sent', 'Sent'), ('PartiallyFilled', 'PartiallyFilled'), ('Filled', 'Filled'), ('DoneForDay', 'DoneForDay'), ('Canceled', 'Canceled'), ('Replaced', 'Replaced'), ('PendingCancel', 'PendingCancel'), ('Stopped', 'Stopped'), ('Rejected', 'Rejected'), ('Suspended', 'Suspended'), ('PendingNew', 'PendingNew'), ('Calculated', 'Calculated'), ('Expired', 'Expired'), ('AcceptedForBidding', 'AcceptedForBidding'), ('PendingReplace', 'PendingReplace'), ('Error', 'Error'), ('Archived', 'Archived')], default='New', db_index=True),
        ),
    ]
