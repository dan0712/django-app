# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0002_auto_20150918_2024'),
    ]

    operations = [
        migrations.RenameField(
            model_name='changedealergroup',
            old_name='daytime_phone_number',
            new_name='work_phone',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='alternate_email_address',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='bulk_investors_spreadsheet',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='fax_number',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='mobile_phone_number',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='office_address_line_1',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='office_address_line_2',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='office_city',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='office_post_code',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='office_state',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='postal_address_line_1',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='postal_address_line_2',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='postal_city',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='postal_post_code',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='postal_state',
        ),
        migrations.RemoveField(
            model_name='changedealergroup',
            name='same_address',
        ),
    ]
