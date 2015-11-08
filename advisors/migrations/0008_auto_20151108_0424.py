# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0007_auto_20151025_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkinvestortransfer',
            name='to_advisor',
            field=models.ForeignKey(verbose_name='To Advisor', to='main.Advisor', related_name='bulk_transfer_to_advisors'),
        ),
        migrations.AlterField(
            model_name='changedealergroup',
            name='letter_new_group',
            field=models.FileField(upload_to='', verbose_name='New Group Letter'),
        ),
        migrations.AlterField(
            model_name='changedealergroup',
            name='letter_previous_group',
            field=models.FileField(upload_to='', verbose_name='Prev. Group Letter'),
        ),
        migrations.AlterField(
            model_name='singleinvestortransfer',
            name='to_advisor',
            field=models.ForeignKey(verbose_name='To Advisor', to='main.Advisor', related_name='single_transfer_to_advisors'),
        ),
    ]
