# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('advisors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='singleinvestortransfer',
            name='from_advisor',
            field=models.ForeignKey(to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='singleinvestortransfer',
            name='investor',
            field=models.ForeignKey(to='main.Client'),
        ),
        migrations.AddField(
            model_name='singleinvestortransfer',
            name='to_advisor',
            field=models.ForeignKey(related_name='single_transfer_to_advisors', to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='changedealergroup',
            name='advisor',
            field=models.ForeignKey(to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='changedealergroup',
            name='new_firm',
            field=models.ForeignKey(related_name='new_advisors', to='main.Firm'),
        ),
        migrations.AddField(
            model_name='changedealergroup',
            name='old_firm',
            field=models.ForeignKey(related_name='old_advisors', to='main.Firm'),
        ),
        migrations.AddField(
            model_name='bulkinvestortransfer',
            name='bulk_investors_spreadsheet',
            field=models.ManyToManyField(to='main.Client'),
        ),
        migrations.AddField(
            model_name='bulkinvestortransfer',
            name='from_advisor',
            field=models.ForeignKey(to='main.Advisor'),
        ),
        migrations.AddField(
            model_name='bulkinvestortransfer',
            name='to_advisor',
            field=models.ForeignKey(related_name='bulk_transfer_to_advisors', to='main.Advisor'),
        ),
    ]
